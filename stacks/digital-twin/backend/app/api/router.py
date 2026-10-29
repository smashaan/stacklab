from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import (
    Component,
    Device,
    DeviceRelationship,
    DeviceType,
    Manufacturer,
    Purchase,
    Room,
    SensorReading,
    Supplier,
)
from ..schemas import (
    Component as ComponentSchema,
    ComponentCreate,
    Device as DeviceSchema,
    DeviceCreate,
    DeviceRelationship as RelationshipSchema,
    DeviceType as DeviceTypeSchema,
    DeviceTypeCreate,
    Manufacturer as ManufacturerSchema,
    ManufacturerCreate,
    Purchase as PurchaseSchema,
    PurchaseCreate,
    RelationshipCreate,
    Room as RoomSchema,
    RoomCreate,
    SensorReading as SensorReadingSchema,
    SensorReadingCreate,
    Summary,
    Supplier as SupplierSchema,
    SupplierCreate,
)
from .auth import get_current_user


router = APIRouter(dependencies=[Depends(get_current_user)])
Database = Annotated[Session, Depends(get_db)]


def save(db: Session, record: object) -> object:
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="The record conflicts with existing data") from error
    return record


def require(db: Session, model: type, record_id: int, label: str):
    record = db.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return record


@router.get("/summary", response_model=Summary, tags=["Dashboard"])
def summary(db: Database) -> Summary:
    return Summary(
        devices=db.scalar(select(func.count()).select_from(Device)) or 0,
        active_devices=db.scalar(select(func.count()).select_from(Device).where(Device.is_active.is_(True))) or 0,
        rooms=db.scalar(select(func.count()).select_from(Room)) or 0,
        components=db.scalar(select(func.count()).select_from(Component)) or 0,
        purchases=db.scalar(select(func.count()).select_from(Purchase)) or 0,
    )


@router.get("/rooms", response_model=list[RoomSchema], tags=["Rooms"])
def list_rooms(db: Database):
    return db.scalars(select(Room).order_by(Room.name)).all()


@router.post("/rooms", response_model=RoomSchema, status_code=status.HTTP_201_CREATED, tags=["Rooms"])
def create_room(payload: RoomCreate, db: Database):
    return save(db, Room(**payload.model_dump()))


@router.get("/devices", response_model=list[DeviceSchema], tags=["Devices"])
def list_devices(
    db: Database,
    room_id: int | None = None,
    device_type_id: int | None = None,
    active: bool | None = None,
):
    query = select(Device).options(
        selectinload(Device.room),
        selectinload(Device.device_type),
        selectinload(Device.manufacturer),
    ).order_by(Device.name)
    if room_id is not None:
        query = query.where(Device.room_id == room_id)
    if device_type_id is not None:
        query = query.where(Device.device_type_id == device_type_id)
    if active is not None:
        query = query.where(Device.is_active == active)
    return db.scalars(query).all()


@router.post("/devices", response_model=DeviceSchema, status_code=status.HTTP_201_CREATED, tags=["Devices"])
def create_device(payload: DeviceCreate, db: Database):
    require(db, DeviceType, payload.device_type_id, "Device type")
    if payload.room_id is not None:
        require(db, Room, payload.room_id, "Room")
    if payload.manufacturer_id is not None:
        require(db, Manufacturer, payload.manufacturer_id, "Manufacturer")
    record = save(db, Device(**payload.model_dump()))
    return db.scalar(
        select(Device)
        .where(Device.id == record.id)
        .options(selectinload(Device.room), selectinload(Device.device_type), selectinload(Device.manufacturer))
    )


@router.get("/components", response_model=list[ComponentSchema], tags=["Components"])
def list_components(db: Database):
    return db.scalars(select(Component).order_by(Component.component_type, Component.model_number)).all()


@router.post("/components", response_model=ComponentSchema, status_code=status.HTTP_201_CREATED, tags=["Components"])
def create_component(payload: ComponentCreate, db: Database):
    return save(db, Component(**payload.model_dump()))


@router.get("/purchases", response_model=list[PurchaseSchema], tags=["Purchases"])
def list_purchases(db: Database):
    return db.scalars(select(Purchase).order_by(Purchase.order_date.desc())).all()


@router.post("/purchases", response_model=PurchaseSchema, status_code=status.HTTP_201_CREATED, tags=["Purchases"])
def create_purchase(payload: PurchaseCreate, db: Database):
    if payload.supplier_id is not None:
        require(db, Supplier, payload.supplier_id, "Supplier")
    return save(db, Purchase(**payload.model_dump()))


@router.get("/lookups/device-types", response_model=list[DeviceTypeSchema], tags=["Lookups"])
def list_device_types(db: Database):
    return db.scalars(select(DeviceType).order_by(DeviceType.name)).all()


@router.post("/lookups/device-types", response_model=DeviceTypeSchema, status_code=201, tags=["Lookups"])
def create_device_type(payload: DeviceTypeCreate, db: Database):
    return save(db, DeviceType(**payload.model_dump()))


@router.get("/lookups/manufacturers", response_model=list[ManufacturerSchema], tags=["Lookups"])
def list_manufacturers(db: Database):
    return db.scalars(select(Manufacturer).order_by(Manufacturer.name)).all()


@router.post("/lookups/manufacturers", response_model=ManufacturerSchema, status_code=201, tags=["Lookups"])
def create_manufacturer(payload: ManufacturerCreate, db: Database):
    return save(db, Manufacturer(**payload.model_dump()))


@router.get("/lookups/suppliers", response_model=list[SupplierSchema], tags=["Lookups"])
def list_suppliers(db: Database):
    return db.scalars(select(Supplier).order_by(Supplier.name)).all()


@router.post("/lookups/suppliers", response_model=SupplierSchema, status_code=201, tags=["Lookups"])
def create_supplier(payload: SupplierCreate, db: Database):
    return save(db, Supplier(**payload.model_dump()))


@router.get("/devices/{device_id}/readings", response_model=list[SensorReadingSchema], tags=["Telemetry"])
def list_readings(
    device_id: int,
    db: Database,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
):
    require(db, Device, device_id, "Device")
    query = select(SensorReading).where(SensorReading.device_id == device_id)
    if start is not None:
        query = query.where(SensorReading.timestamp >= start)
    if end is not None:
        query = query.where(SensorReading.timestamp <= end)
    return db.scalars(query.order_by(SensorReading.timestamp.desc()).limit(limit)).all()


@router.post("/devices/{device_id}/readings", response_model=SensorReadingSchema, status_code=201, tags=["Telemetry"])
def create_reading(device_id: int, payload: SensorReadingCreate, db: Database):
    require(db, Device, device_id, "Device")
    return save(db, SensorReading(device_id=device_id, **payload.model_dump()))


@router.post("/devices/{device_id}/relationships", response_model=RelationshipSchema, status_code=201, tags=["Relationships"])
def create_relationship(device_id: int, payload: RelationshipCreate, db: Database):
    require(db, Device, device_id, "Parent device")
    require(db, Device, payload.child_device_id, "Child device")
    if device_id == payload.child_device_id:
        raise HTTPException(status_code=422, detail="A device cannot relate to itself")
    return save(db, DeviceRelationship(parent_device_id=device_id, **payload.model_dump()))

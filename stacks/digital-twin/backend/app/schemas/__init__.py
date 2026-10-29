from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Summary(BaseModel):
    devices: int
    active_devices: int
    rooms: int
    components: int
    purchases: int


class LookupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class DeviceTypeCreate(LookupCreate):
    description: str | None = None


class DeviceType(DeviceTypeCreate, ORMModel):
    id: int


class ManufacturerCreate(LookupCreate):
    country: str | None = Field(default=None, max_length=100)
    website: str | None = None


class Manufacturer(ManufacturerCreate, ORMModel):
    id: int


class SupplierCreate(LookupCreate):
    website: str | None = None


class Supplier(SupplierCreate, ORMModel):
    id: int


class RoomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    floor: int | None = None
    description: str | None = None


class Room(RoomCreate, ORMModel):
    id: int


class PurchaseCreate(BaseModel):
    supplier_id: int | None = None
    order_date: date
    arrival_date: date | None = None
    order_number: str | None = Field(default=None, max_length=255)
    total_price: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None


class Purchase(PurchaseCreate, ORMModel):
    id: int
    created_at: datetime


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    device_type_id: int
    manufacturer_id: int | None = None
    room_id: int | None = None
    purchase_id: int | None = None
    model_number: str | None = Field(default=None, max_length=255)
    serial_number: str | None = Field(default=None, max_length=255)
    ip_address: str | None = Field(default=None, max_length=45)
    mac_address: str | None = Field(default=None, max_length=17)
    is_active: bool = True
    status: str = Field(default="operational", min_length=1, max_length=50)
    notes: str | None = None


class Device(DeviceCreate, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime
    room: Room | None = None
    device_type: DeviceType
    manufacturer: Manufacturer | None = None


class ComponentCreate(BaseModel):
    component_type: str = Field(min_length=1, max_length=100)
    manufacturer_id: int | None = None
    purchase_id: int | None = None
    model_number: str | None = Field(default=None, max_length=255)
    specifications: dict | None = None
    notes: str | None = None


class Component(ComponentCreate, ORMModel):
    id: int


class SensorReadingCreate(BaseModel):
    reading_type: str = Field(min_length=1, max_length=100)
    value: Decimal


class SensorReading(SensorReadingCreate, ORMModel):
    id: int
    device_id: int
    timestamp: datetime


class RelationshipCreate(BaseModel):
    child_device_id: int
    relationship_type: str = Field(min_length=1, max_length=100)


class DeviceRelationship(RelationshipCreate, ORMModel):
    parent_device_id: int

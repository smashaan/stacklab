module.exports = {
    credentialSecret: process.env.NODE_RED_CREDENTIAL_SECRET,

    adminAuth: {
        type: "credentials",
        users: [
            {
                username: process.env.NODE_RED_ADMIN_USER,
                password: process.env.NODE_RED_ADMIN_PASSWORD_HASH,
                permissions: "*"
            }
        ]
    },

    editorTheme: {
        projects: {
            enabled: process.env.NODE_RED_ENABLE_PROJECTS === "true"
        }
    }
};

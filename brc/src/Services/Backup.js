const execSync = require("child_process").execSync;

const path = "./Tests/mydatabase_backup.sql";

// backup command
const output = execSync(
    "mysqldump -u root -psid34 siddata > " + path,
    { encoding: "utf-8" }
);

console.log("Output was:", output);

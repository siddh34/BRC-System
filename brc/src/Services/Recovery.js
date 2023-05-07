const execSync = require("child_process").execSync;

// Recorvery command

let path = "./Tests/mydatabase_backup1.sql";

const recovery = execSync(
    "mysql -u root -p siddata < " + path,
    { encoding: "utf-8" }
);

console.log("Output was:", recovery);
// get the client
const mysql = require("mysql2");
const execSync = require("child_process").execSync;

// create the connection to database
const connection = mysql.createConnection({
    host: "localhost",
    user: "root",
    database: "siddata",
    password: "sid34",
});

// Display query
connection.query("SELECT * FROM client;", function (err, results, fields) {
    console.log(results); // results contains rows returned by server
    // console.log(fields); // fields contains extra meta data about results, if available
    console.log("Done!");
});

// backup command
const output = execSync(
    "mysqldump -u root -psid34 siddata > ./Tests/mydatabase_backup.sql",
    { encoding: "utf-8" }
);
console.log("Output was:", output);


const recovery = execSync(
    "mysql -u root -p siddata < ./Tests/mydatabase_backup.sql",
    { encoding: "utf-8" }
);
console.log("Output was:", recovery);



connection.end();

const mysql = require("mysql2");

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

connection.end();
const express = require('express');
const { exec } = require('child_process');

const app = express();

app.get('./api/ls', (req, res) => {
  exec('ls', (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      res.status(500).send('Server error');
      return;
    }

    if (stderr) {
      console.error(`stderr: ${stderr}`);
      res.status(500).send('Server error');
      return;
    }

    console.log(req);
    res.send(stdout);
});
});

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
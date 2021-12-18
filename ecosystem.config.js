module.exports = {
  apps: [{
    name: "sensor-hub",
    script: "sensor-hub.py",
    interpreter: "/usr/bin/python3",
    cwd: '.',
    watch: true
  }]
}

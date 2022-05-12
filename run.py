from blue_shell_main import app

# To kill off, first search pid using: ps -fA | grep python
# Then after getting the pid, use: kill -9 [pid]

if __name__ == "__main__":
    app.run()
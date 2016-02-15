from flask.ext.script import Manager

from app import app

manager = Manager(app)

@manager.command
def runworker():
    from app import cronjobs
    job = cronjobs.AirportDelayRetriever()
    job.run()

if __name__ == "__main__":
    manager.run()

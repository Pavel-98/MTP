import time

class TimeReporter:

    def __init__(self):
        self.events = []
        self.timestamp = time.time()

    def report_time(self, event_name):
        now = time.time()
        self.events.append({'name': event_name, 'time': round(now - self.timestamp, 3)})
        self.timestamp = now

    def get_report(self):
        report = '\n'
        total_time = 0
        for event in self.events:
            name = event['name']
            time = event['time']
            total_time += time
            report += f'\n{name}: {time} s.'
        return report + f'\nTotal time: {round(total_time, 3)} s.'

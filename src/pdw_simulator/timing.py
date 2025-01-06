import time
import functools
from contextlib import contextmanager
import yaml
from collections import defaultdict

class SimulationTimer:
    def __init__(self):
        self.timings = defaultdict(float)
        self.start_times = {}
        self.total_start = None
        
    @contextmanager
    def time_section(self, section_name):
        """Context manager to time a section of code"""
        start = time.perf_counter()
        try:
            yield
        finally:
            self.timings[section_name] += time.perf_counter() - start
            
    def start_timer(self):
        """Start the overall simulation timer"""
        self.total_start = time.perf_counter()
        
    def get_total_time(self):
        """Get the total simulation time"""
        if self.total_start is None:
            return 0
        return time.perf_counter() - self.total_start
    
    def print_report(self):
        """Print a detailed timing report"""
        total_time = self.get_total_time()
        print("\n=== Performance Report ===")
        print(f"Total Simulation Time: {total_time:.4f} seconds")
        print("\nDetailed Breakdown:")
        print("-" * 40)
        
        # Calculate percentages and sort by time
        sorted_timings = sorted(
            [(name, time_taken, (time_taken/total_time)*100) 
             for name, time_taken in self.timings.items()],
            key=lambda x: x[1], reverse=True
        )
        
        for name, time_taken, percentage in sorted_timings:
            print(f"{name:25s}: {time_taken:8.4f}s ({percentage:5.1f}%)")
            
    def save_report(self, filename):
        """Save timing report to a YAML file"""
        report = {
            'total_time': self.get_total_time(),
            'section_timings': dict(self.timings)
        }
        with open(filename, 'w') as f:
            yaml.dump(report, f)

# Example usage in main.py:
"""
def main():
    # Initialize timer
    timer = SimulationTimer()
    timer.start_timer()
    
    # Load configuration
    with timer.time_section("Configuration Loading"):
        config = load_config('dataconfig.yaml')
        scenario = create_scenario(config)
    
    # Run simulation with timing
    with timer.time_section("Simulation Execution"):
        while scenario.current_time <= scenario.end_time:
            with timer.time_section("Time Step Processing"):
                scenario.update()
                
            with timer.time_section("PDW Generation"):
                for sensor in scenario.sensors:
                    for radar in scenario.radars:
                        pdw = generate_pdw(sensor, radar, scenario.current_time)
                        if pdw:
                            # Process PDW...
                            pass
                            
            scenario.current_time += scenario.time_step
    
    # Print timing report
    timer.print_report()
    
    # Save report to file
    timer.save_report('simulation_timing.yaml')

if __name__ == "__main__":
    main()
"""
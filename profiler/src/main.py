from src import profiling_scripts as ps

profiler = ps.Profiler()
profiler.run('../user_history.json', '../articles.json')


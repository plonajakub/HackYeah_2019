from src import profiling_scripts as ps

profiler = ps.Profiler()
profiler.run('../data/user_history.json', '../data/articles.json')


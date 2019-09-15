import json

from profiler.src import profiling_scripts as ps

with open('../data/user_history.json') as f:
    user_history = json.load(f)
with open('../data/articles.json') as f:
    articles = json.load(f)

profiler = ps.Profiler()
print(profiler.run(user_history, articles))

import os, re, datetime

import easygraph


CATEGORIES = 'improvement', 'networking', 'job', 'obligations', 'sick', 'startup'
path = os.path.expanduser('~/Dropbox/notational_velocity_notes/time budget (debt) (work done).txt')

with open(path) as f:
  text = f.read()

lines = text.splitlines()
budget_vals = []
dates = []
budget = 0
fixed_lines = []
year = 2016
goal_hours_per_day = 9  # 9 * 7 = 63 hours per week
incremented_year = False
category_to_hours = {}
daily_hours = []
normal_line_count = 0

# Iterate each non-comment line in the file.

for line in lines[::-1]:
  try:
    if line.startswith('//') or not line.strip():
      fixed_lines.append(line)
      continue
    if line.startswith('-- '):
      continue

    # 01/21; -21.5; 4 hours networking; .5 hours improvement
    # <date>; <budget>; (<n> hours <category>)+

    # Parse date

    vals = [s for s in re.split(';|,', line)]
    print 'vals:', vals

    date_str = vals[0]
    month, date = (int(s) for s in date_str.split('/'))
    if month == 1 and date == 1:
      year += 1
    dates.append(datetime.datetime(year, month, date))

    # Parse job values

    job_vals = vals[2:]
    categories = [re.sub('[0-9\.]+( hours?)?', '', job_val).strip() for job_val in job_vals]
    hours_list = [float(re.search('[0-9\.]+', s).group()) for s in job_vals]
    for category, hours in zip(categories, hours_list):
      if not category:
        continue
      if category not in CATEGORIES:
        raise Exception("Job not matched: " + category)
      category_to_hours.setdefault(category, 0)
      category_to_hours[category] += hours
    budget += sum(hours_list) - goal_hours_per_day
    fixed_line = '; '.join([str(x).strip() for x in [date_str, budget] + job_vals])
    fixed_lines.append(fixed_line)
    budget_vals.append(budget)
    daily_hours.append(sum(hours_list))
  except:
    print 'fail:', line
    raise

# Create hour-per-category summary.

print 'category_to_hours:', sorted(category_to_hours.iteritems(), key=lambda x: x[-1])
total_hours = sum(category_to_hours.values())
for category, value in sorted(category_to_hours.iteritems(), key=lambda t: t[1]):
  percent_line = str(int(round(value / total_hours * 100))) + '%', category, value
  fixed_lines.append('-- {}'.format(percent_line))
  print percent_line

fixed_lines = fixed_lines[::-1]

# Insert the seven day mark.

normal_line_count = 0
for i, line in enumerate(fixed_lines):
  if line.startswith('//') or line.startswith('-- ') or not line.strip():
    continue
  normal_line_count += 1
  if normal_line_count == 8:
    fixed_lines.insert(i, '-- seven days --')
    break

# Rewrite time-log and graph.

with open(path, 'w') as f:
  f.write('\n'.join(fixed_lines))

easygraph.graph(zip(dates, budget_vals), show_lines=True,
                labels=[line for line in fixed_lines[::-1] if re.search('^[0-9]', line)])
# easygraph.graph(zip(dates, daily_hours), show_lines=True, labels=fixed_lines)
# easygraph.graph(
#   zip([dates[i] for i in range(0, len(dates), 7)][:-1],
#       [sum(daily_hours[i:i + 7]) for i in range(0, len(daily_hours), 7)][:-1]),
#   show_lines=True, labels=fixed_lines)

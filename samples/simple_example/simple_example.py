import matplotlib.pyplot as plt
import seaborn as sns
import FragStatsPy.frag_model as fspy

model = fspy.FragModel(r'samples\simple_example\simple_model.fca')

model.load_landscape_layer(r"samples\simple_example\classes.tif")

model.set_output_base_path(r'samples\simple_example\model_outputs')

model.set_user_provided_tiles(r"samples\simple_example\user_tiles.tif")
model.set_sampling_strategy(strategy='user_tiles', landscape=True, class_=True)


model.toggle_metric(level='c', metric='PLAND')
model.toggle_metric(level='c', metric='ED')
model.toggle_metric(level='c', metric='AREA_MN')

model.toggle_metric(level='l', metric='TA')


model.run_model()
results = model.get_results()

# parse some results and prepare for plotting
results['class']['user_tile'] = results['class']['LID'].apply(lambda s: int(s.split('\\')[-1]))
results['land']['user_tile'] = results['land']['LID'].apply(lambda s: int(s.split('\\')[-1]))
results['class'] = results['class'].sort_values('TYPE')

# Plot
sns.barplot(x='user_tile', hue='TYPE', y='PLAND', data=results['class'], palette = 'hls')
plt.show()

sns.barplot(x='user_tile', hue='TYPE', y='ED', data=results['class'], palette = 'hls')
plt.show()

sns.barplot(x='user_tile', hue='TYPE', y='AREA_MN', data=results['class'], palette = 'hls')
plt.show()

sns.barplot(x='user_tile', y='TA', data=results['land'], palette = 'hls')
plt.show()
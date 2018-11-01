blender --background --python render_images.py -- --num_images 2000 --render_num_samples 128 --use_gpu 1 --min_objects 5 --max_objects 5 --min_pixels_per_object 200 --min_dist 1.25 --properties_json data/simpl
e_properties.json --base_scene_blendfile data/base_scene.blend --margin 0.1 --split train --start_idx 6000

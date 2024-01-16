import tensorflow as tf


# saved_model_dir = 'model_trained/old_blilstm/blilstm'
saved_model_dir = 'model_trained/blilstm'

model_filename = 'model.tflite'

# saved_model_dir = 'model_trained/old_blilstm'
genereate_model_dir = 'model_trained/'

# Convert the model.
converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)

converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]
converter._experimental_lower_tensor_list_ops = False

tflite_model = converter.convert()

# Save the model.
with open(genereate_model_dir + model_filename, 'wb') as f:
  f.write(tflite_model)



# xxd -i converted_model.tflite > model_data.cc     
# 一旦你已经生成了此文件，你可以将它包含入你的程序。在嵌入式平台上，将数组声明改变为 const 类型以获得更好的内存效率是重要的。
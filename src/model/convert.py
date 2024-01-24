import tensorflow as tf

# Convert the model
converter = tf.lite.TFLiteConverter.from_saved_model('/home/mqiu/hongmin_new/two/result/1220/1904/test100_1.pb') # path to the SavedModel directory
tflite_model = converter.convert()

# Save the model.
with open('/home/mqiu/hongmin_new/two/result/1220/1904/test100_1_S.tflite', 'wb') as f:
  f.write(tflite_model)
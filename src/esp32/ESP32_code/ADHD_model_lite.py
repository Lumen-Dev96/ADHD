# Microlite implementation of the tensorflow hello-world example
# https://github.com/tensorflow/tensorflow/tree/master/tensorflow/lite/micro/examples/hello_world
import microlite
import io

hello_world_model = bytearray(33000)
model_file = io.open('model.tflite', 'rb')
model_file.readinto(hello_world_model)
model_file.close()



class MyModel():
    def __init__(self, input):
        self.input = input
        self.init()

    def init(self):
        self.interp = microlite.interpreter(hello_world_model,10*1024, self.input_callback, self.output_callback)


    def input_callback (self, microlite_interpreter):

        inputTensor = microlite_interpreter.getInputTensor(0)
        counter = 0

        for mpu_data_vector in self.input:
            for data in mpu_data_vector:
                inputTensor.setValue(counter, data)
                counter = counter + 1

    def output_callback (self, microlite_interpreter):

        outputTensor = microlite_interpreter.getOutputTensor(0)

        # print (outputTensor)

        max_ = float(0)
        posture = 0
        for i in range(14):
            y = outputTensor.getValue(i)
            print(y)
            if y > max_:
                max_ = y
                posture = i + 1

        #y = outputTensor.quantizeInt8ToFloat(y_quantized)

        #print ("%f,%f" % (current_input,y))
        print (max_, posture)


    def run_model(self):
        # print ("time step,y")
        self.interp.invoke()
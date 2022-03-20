import numpy as np
import onnx
import onnxruntime as ort
from onnx import numpy_helper

model_path = "Foosball.onnx"

velocityScalar = 8
maxPosition = 3.6125
maxAcceleration = 3
foosLinearVelocity = 0
fixedDeltaTime = 0.02

def rawInputToUnity(inputArray):
    linearInput = velocityScalar*inputArray[0]

    if (foosLinearVelocity - linearInput) > maxAcceleration: #slowing down too fast forward or speeding up too fast backwards
        foosLinearVelocity = foosLinearVelocity - maxAcceleration
    elif (linearInput - foosLinearVelocity) > maxAcceleration: #slowing down too fast backward or speeding up too fast forward
        foosLinearVelocity = foosLinearVelocity + maxAcceleration
    else:
        foosLinearVelocity = linearInput
    


testdata = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
onnx_model = onnx.load(model_path)
onnx.checker.check_model(onnx_model)

#print([input.name for input in onnx_model.graph.input])
#print([output.name for output in onnx_model.graph.output])

ort_sess = ort.InferenceSession("Foosball.onnx")

outputs = ort_sess.run(["continuous_actions"], {'obs_0': testdata}) #None returns all of the outputs

print(outputs) #This is going to print out the output weights, check unity for the rest of the translation



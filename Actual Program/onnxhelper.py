import numpy as np
import onnx
import onnxruntime as ort
from onnx import numpy_helper

class OnnxHelper():
    def __init__(self):
        self.model_path = "Foosball.onnx"

        self.velocityScalar = 8
        self.maxPosition = 3.6125
        self.maxAcceleration = 3
        self.foosLinearVelocity = 0
        self.fixedDeltaTime = 0.02
        self.unityZScalar = 4.25

    def setInputs(self, ballPos, rodPosArray, rodRotArray):
        toBall = np.array([(ballPos[1] - rodPosArray[1][1])*self.unityZScalar, 0, (ballPos[0] - rodPosArray[1][0]*self.unityZScalar)])
        #A few things to note: rodPosArray[1] refers to 2nd closest to top of frame (id 1)
        #Unity's system is [our height, 0, our width] or [y, 0, x]
        toBallMagnitude = np.linalg.norm(toBall)
        toBallNormalized = toBall/toBallMagnitude
        
        agentPlayerPos = rodPosArray[1]*self.unityZScalar
        agentRotPos = rodRotArray[1]
        #to ball.normalized (3)
        #to ball.magnitude (1)
        #agent.position (1)
        #agent.rotation (1)
        #enemyagent.position (1)
        pass
    
    def runOnnx(self, testdata):
        testdata = np.array(testdata, dtype=np.float32)
        onnx_model = onnx.load(self.model_path)
        onnx.checker.check_model(onnx_model)

        #print([input.name for input in onnx_model.graph.input])
        #print([output.name for output in onnx_model.graph.output])

        ort_sess = ort.InferenceSession("Foosball.onnx")

        outputs = ort_sess.run(["continuous_actions"], {'obs_0': testdata}) #None returns all of the outputs

        print(outputs) #This is going to print out the output weights, check unity for the rest of the translation

    def rawOutputToUnity(self, inputArray):
            linearInput = self.velocityScalar * inputArray[0]

            if (foosLinearVelocity - linearInput) > self.maxAcceleration: #slowing down too fast forward or speeding up too fast backwards
                foosLinearVelocity = foosLinearVelocity - self.maxAcceleration
            elif (linearInput - foosLinearVelocity) > self.maxAcceleration: #slowing down too fast backward or speeding up too fast forward
                foosLinearVelocity = foosLinearVelocity + self.maxAcceleration
            else:
                foosLinearVelocity = linearInput

import numpy as np
import onnx
import onnxruntime as ort
#from onnx import numpy_helper

class OnnxHelper():

    def __init__(self):
        self.model_path = "spfoos.onnx"
        self.maxPosition = 3.6125
        self.maxRotation = 45
        self.foosLinearVelocity = 0
        self.foosAngularVelocity = 0
        self.fixedDeltaTime = 0.02
        self.unityZScalar = 4.25
        self.lastInput = 0
        self.lastInput = 0

        self.linearInput = 0
        self.rotaryInput = 0

        onnx_model = onnx.load(self.model_path)
        onnx.checker.check_model(onnx_model)

    def correctRodPos(self, rodPosArray):
        pass #this will adjust for the dist of where things are placed

    def setInputs(self, ballPos, rodPosArray, rodRotArray):
        self.lastInput = np.array([*toBallNormalized, toBallMagnitude, agentPos, agentRot, enemyPos], dtype=np.float32)

        toBall = np.array([(ballPos[1] - rodPosArray[1][1])*self.unityZScalar, 0, (ballPos[0] - rodPosArray[1][0]*self.unityZScalar)])
        #A few things to note: rodPosArray[1] refers to 2nd closest to top of frame (id 1)
        #Unity's system is [our height, 0, our width] or [y, 0, x]
        toBallMagnitude = np.linalg.norm(toBall) 
        toBallNormalized = toBall/toBallMagnitude
        
        agentPos = rodPosArray[1]*self.unityZScalar
        agentRot = rodRotArray[1]

        enemyPos = rodPosArray[0]*self.unityZScalar        
    
        return np.array([*toBallNormalized, toBallMagnitude, agentPos, agentRot, enemyPos], dtype=np.float32)
        #to ball.normalized (3)
        #to ball.magnitude (1)
        #agent.position (1)
        #agent.rotation (1)
        #enemyagent.position (1)
    
    def runOnnx(self, ballPos, rodPosArray, rodRotArray):

        self.input = self.setInputs(ballPos, rodPosArray, rodRotArray)

        totalInputs = np.concatenate(self.input, self.lastInput, axis=0)
        

        #print([input.name for input in onnx_model.graph.input])
        #print([output.name for output in onnx_model.graph.output])
        ort_sess = ort.InferenceSession("Foosball.onnx")

        outputs = ort_sess.run(["continuous_actions"], {'obs_0': totalInputs}) #None returns all of the outputs

        linVel, rotVel = self.rawOutputToVel(self, rodPosArray, rodRotArray, outputs)

        linSteps, rotSteps = self.velToSteps(linVel, rotVel)
        
        return linSteps, rotSteps

    def rawOutputToVel(self, rodPosArray, rodRotArray, outputArray): #currently only for one rod
        if (outputArray[0] == 0):
            self.linearInput -= 1
        elif (outputArray[0] == 2):
            self.linearInput += 1

        if (outputArray[1] == 0):
            self.rotaryInput -= 1
        elif (outputArray[1] == 2):
            self.rotaryInput += 1


        if (self.linearInput >= 3):
            self.linearInput = 3
            self.foosLinearVelocity = 30
        elif (self.linearInput == 2):
            self.foosLinearVelocity = 8
        elif (self.linearInput == 1):
            self.foosLinearVelocity = 2
        elif (self.linearInput == 0):
            self.foosLinearVelocity = 0
        elif (self.linearInput == -1):
            self.foosLinearVelocity = -2
        elif (self.linearInput == -2):
            self.foosLinearVelocity = -8
        else:
            self.linearInput = -2
            self.foosLinearVelocity = -30


        if (self.rotaryInput >= 2):
            self.rotaryInput = 2
            self.foosAngularVelocity = 450
        elif (self.rotaryInput == 1):
            self.foosAngularVelocity = 90
        elif (self.rotaryInput == 0):
            self.foosAngularVelocity = 0
        elif (self.rotaryInput == -1):
            self.foosAngularVelocity = -90
        else:
            self.rotaryInput = -2
            self.foosAngularVelocity = -450
    
        newRodPosArray = rodPosArray
        newRodPosArray[1] = rodPosArray[1] + self.foosLinearVelocity * self.fixedDeltaTime
        if newRodPosArray[1] > self.maxPosition:
            newRodPosArray[1] = self.maxPosition
            self.foosLinearVelocity = 0
            self.linearInput = 0
        elif newRodPosArray[1] < -1*self.maxPosition:
            newRodPosArray[1] = -1*self.maxPosition
            self.foosLinearVelocity = 0
            self.linearInput = 0

        newRodRotArray = rodRotArray
        newRodRotArray[1] = rodRotArray[1] + self.foosAngularVelocity * self.fixedDeltaTime
        if newRodRotArray[1] > self.maxRotation and newRodRotArray < 180:
            newRodRotArray[1] = self.maxRotation
            self.foosAngularVelocity = 0
            self.rotaryInput = 0
        elif newRodRotArray[1] < 360-1*self.maxRotation:
            newRodRotArray[1] = 360-1*self.maxPosition #think about this more later
            self.foosLinearVelocity = 0
            self.rotaryInput = 0

        return self.foosLinearVelocity, self.foosAngularVelocity

    def velToSteps(self, lin, rot):
        #to change speed to steps:
        linSteps = int(lin / 6.28 * 200 * self.fixedDeltaTime) #divide by circumference, multiply by steps, times deltaTime
        rotSteps = int(rot * 200 / 360 * self.fixedDeltaTime) #multiply by steps, divided by degrees, times deltaTime

        return linSteps, rotSteps

    def stepsToRot(self, steps):
        #to change steps to speed:
        rot = int(steps / 200 * 360)
        return rot
        

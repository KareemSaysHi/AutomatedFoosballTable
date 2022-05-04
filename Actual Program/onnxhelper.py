from pydoc import Helper
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

        onnx_model = onnx.load(self.model_path)
        onnx.checker.check_model(onnx_model)

        self.linearInput = 0
        self.rotaryInput = 0

        #three player variables

        self.linearInputs = [0, 0, 0]
        self.rotaryInputs = [0, 0, 0]

        self.linearVelocityOffense = 0
        self.linearVelocityMid = 0 
        self.linearVelocityDefense = 0

        self.linearVelocities = [self.linearVelocityOffense, self.linearVelocityMid, 
        self.linearVelocityDefense]

        self.angularVelocityOffense = 0
        self.angularVelocityMid = 0
        self.angularVelocityDefense = 0

        self.angularVelocities = [self.angularVelocityOffense, self.angularVelocityMid, 
        self.angularVelocityDefense]

        self.maxPosArray = [3.6125, 2.5, 3.6125]

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

    def setInputsThrees(self, ballPos, rodPosArray, rodRotArray):
        self.lastInput = np.array([*toBallNormalized, toBallMagnitude, agentPos, agentRot, enemyPos], dtype=np.float32)

        toBall = np.array([(ballPos[1] - rodPosArray[1][1])*self.unityZScalar, 0, (ballPos[0] - rodPosArray[1][0]*self.unityZScalar)])
        #A few things to note: rodPosArray[1] refers to 2nd closest to top of frame (id 1)
        #Unity's system is [our height, 0, our width] or [y, 0, x]
        toBallMagnitude = np.linalg.norm(toBall) 
        toBallNormalized = toBall/toBallMagnitude
        
        agentPos = rodPosArray[1]*self.unityZScalar
        agentRot = rodRotArray[1]

        enemyPos = rodPosArray[0]*self.unityZScalar        
    
        return np.array([*toBallNormalized, toBallMagnitude, rodPosArray[1][1], rodPosArray[3][1], rodPosArray[5][1], rodPosArray[1], rodPosArray[3], rodPosArray[5], rodPosArray[0][1], rodPosArray[2][1], rodPosArray[4][1]], dtype=np.float32)
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

    def runOnnxThrees(self, ballPos, rodPosArray, rodRotArray, heuristic = False, manufacturedOutput = []):

        if not heuristic:
            
            self.input = self.setInputsThrees(ballPos, rodPosArray, rodRotArray)

            totalInputs = np.concatenate(self.input, self.lastInput, axis=0)
            

            #print([input.name for input in onnx_model.graph.input])
            #print([output.name for output in onnx_model.graph.output])
            ort_sess = ort.InferenceSession("Foosball.onnx")

            outputs = ort_sess.run(["continuous_actions"], {'obs_0': totalInputs}) #None returns all of the outputs
        
        if heuristic:
            outputs = manufacturedOutput

        linoff, linmid, lindef, rotoff, rotmid, rotdef = self.rawOutputToVelThrees(self, rodPosArray, rodRotArray, outputs)

        linoffSteps, rotoffSteps = self.velToSteps(linoff, rotoff)

        linmidSteps, rotmidSteps = self.velToSteps(linmid, rotmid)

        lindefSteps, rotdefSteps = self.velToSteps(lindef, rotdef)
        
        return linoffSteps, linmidSteps, lindefSteps, rotoffSteps, rotmidSteps, rotdefSteps

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

    def rawOutputToVelThrees(self, rodPosArray, rodRotArray, outputArray): #this one works for three

        players = [1, 3, 5]
        
        for i in range (0, 3):
            if outputArray[i] == 0:
                self.linearInputs[i] -= 1
            elif outputArray[i] == 2:
                self.linearInputs[i] += 1

        for i in range (3, 6):
            if outputArray[i] == 0:
                self.rotaryInputs[i-3] -= 1
            elif outputArray[i] == 2:
                self.rotaryInputs[i-3] += 1
                
        for i in range (0, 3):
            if (self.linearInputs[i] >= 3):
                self.linearInputs[i] = 3
                self.linearVelocities[i] = 30
            elif (self.linearInput == 2):
                self.linearVelocities[i] = 8
            elif (self.linearInput == 1):
                self.linearVelocities[i] = 2
            elif (self.linearInput == 0):
                self.linearVelocities[i] = 0
            elif (self.linearInput == -1):
                self.linearVelocities[i] = -2
            elif (self.linearInput == -2):
                self.linearVelocities[i] = -8
            else:
                self.linearInputs[i] = -2
                self.linearVelocities[i] = -30

            newRodPosArray = rodPosArray #copy over
            newRodPosArray[players[i]] = rodPosArray[players[i]] + self.linearVelocities[i] * self.fixedDeltaTime #update
            if newRodPosArray[players[i]] > self.maxPosArray[i]: #if outside
                newRodPosArray[players[i]] = self.maxPosition #fix
                self.linearVelocities[i] = 0
                self.linearInputs[i] = 0
            elif newRodPosArray[players[i]] < -1*self.maxPosArray[i]:
                newRodPosArray[players[i]] = -1*self.maxPosArray[i]
                self.linearVelocities[i] = 0
                self.linearInputs[i] = 0

        for j in range (0, 3):
            if (self.rotaryInputs[j] >= 2):
                self.rotaryInputs[j] = 2
                self.angularVelocities[j] = 450
            elif (self.rotaryInputs[j] == 1):
                self.angularVelocities[j] = 90
            elif (self.rotaryInputs[j] == 0):
                self.angularVelocities[j] = 0
            elif (self.rotaryInputs[j] == -1):
                self.angularVelocities[j] = -90
            else:
                self.rotaryInputs[j] = -2
                self.angularVelocities[j] = -450        

            newRodRotArray = rodRotArray #copy
            newRodRotArray[players[j]] = rodRotArray[players[j]] + self.angularVelocities[j] * self.fixedDeltaTime #update
            if newRodRotArray[players[j]] > self.maxRotation and newRodRotArray[players[j]] < 180:
                newRodRotArray[players[j]] = self.maxRotation
                self.angularVelocities[j] = 0
                self.rotaryInputs[j] = 0
            elif newRodRotArray[players[j]] < 360-1*self.maxRotation:
                newRodRotArray[1] = 360-1*self.maxRotation #think about this more later
                self.angularVelocities[j] = 0
                self.rotaryInputs[j] = 0

        return [*self.linearVelocites, *self.angularVelocities]


    def velToSteps(self, lin, rot):
        #to change speed to steps:
        linSteps = int(lin / 6.28 * 200 * self.fixedDeltaTime) #divide by circumference, multiply by steps, times deltaTime
        rotSteps = int(rot * 200 / 360 * self.fixedDeltaTime) #multiply by steps, divided by degrees, times deltaTime

        return linSteps, rotSteps

    def stepsToRot(self, steps):
        #to change steps to speed:
        rot = int(steps / 200 * 360)
        return rot
        

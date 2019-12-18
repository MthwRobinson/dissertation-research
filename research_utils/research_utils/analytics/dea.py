import pulp
import pandas as pd
import numpy as np

def build_example():
    df_dict = {
        'meals_sold' : [100,100,100,100,100,100],
        'labor_hours' : [2,4,4,6,8,10],
        'material_dollars' : [200,150,100,100,80,50]
    }
    df = pd.DataFrame(df_dict)
    return df

class DEA_Error(Exception):
    """
    DEA_Error Class
    Defines a custom error message for exceptions relating
    to the DEA class
    """
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return repr(self.value)

class DEA():
    def __init__(self, inputs, outputs, model = 'input'):

        max_models = ['output', 'ccr']
        min_models = ['input']

        if type(inputs) == np.ndarray:
            self.inputs = inputs
        else:
            self.inputs = np.array(inputs)
            if len(self.inputs.shape) == 0:
                error = "Inputs must be an array-like object"
                raise DEA_Error(error)

        if type(outputs) == np.ndarray:
            self.outputs = outputs
        else:
            self.outputs = np.array(outputs)
            if len(self.outputs.shape) == 0:
                error = "Outputs must be an array-like object"
                raise DEA_Error(error)

        if self.inputs.shape[0] != self.outputs.shape[0]:
            error = "Inputs and outputs must have the same number of rows"
            raise DEA_Error(error)

        self.model = model
        self.num_inputs = self.inputs.shape[1]
        self.num_outputs = self.outputs.shape[1]
        self.num_dmus = self.inputs.shape[0]
        if self.model in min_models: 
            self.lp_list = [pulp.LpProblem("DMU "+str(j), pulp.LpMinimize)
                    for j in range(self.num_dmus)]
        elif self.model in max_models:
            self.lp_list = [pulp.LpProblem("DMU "+str(j), pulp.LpMaximize)
                    for j in range(self.num_dmus)]

        self._build_variables()
        self._formulate_lp()


    def _build_variables(self):
        """
        Builds the variables to include in the ccr model
        y_rj : amount of output r produced by DMU j
        x_ij : amount of input i used by DMU j
        z_j : weight given to DMU j
        u_r : weight given to output r
        v_r : weight given to input i
        """

        # Build outputs
        y = []
        u = []
        for j, dmu in enumerate(self.outputs):
            dmu_outputs = []
            for r, output in enumerate(dmu):
                dmu_outputs.append(output)
                if j == 1:
                    var = 'u_' + str(r)
                    lp_var = pulp.LpVariable(var, lowBound = 0, 
                            cat = 'Continuous')
                    u.append(lp_var)
            y.append(dmu_outputs)
        y = np.array(y)
        y = y.transpose()
        self.y = y
        u = np.array(u)
        self.u = u

        # Build inputs
        x = []
        v = []
        for j, dmu in enumerate(self.inputs):
            dmu_inputs = []
            for i, input in enumerate(dmu):
                dmu_inputs.append(input)
                if j == 1:
                    var = 'v_' + str(i)
                    lp_var = pulp.LpVariable(var, lowBound = 0, 
                            cat = 'Continuous')
                    v.append(lp_var)
            x.append(dmu_inputs)
        x = np.array(x)
        x = x.transpose()
        self.x = x
        v = np.array(v)
        self.v = v

        # Build weights
        z = []
        for j, dmu in enumerate(self.inputs):
            var = 'z_' + str(j)
            lp_var = pulp.LpVariable(var, lowBound = 0, 
                    cat = 'Continuous')
            z.append(lp_var)
        z = np.array(z)
        self.z = z

    def _formulate_lp(self):
        if self.model == 'input':
            self._formulate_input_lp()
        elif self.model == 'output':
            self._formulate_output_lp()
        elif self.model == 'ccr':
            self._formulate_ccr_lp()

    def _formulate_input_lp(self):
        y = self.y; u = self.u
        x = self.x; v = self.v
        z = self.z

        # Input reducing model
        for j, lp in enumerate(self.lp_list):

            # Build objective function
            E = pulp.LpVariable('E', lowBound = 0, 
                    cat = 'Continuous')
            lp += E, 'E'

            # Build constraints
            for i in range(self.num_inputs):
                f = 0
                for jj in range(self.num_dmus):
                    f += x[i][jj]*z[jj]
                lp += f <= E*x[i][j]

            for r in range(self.num_outputs):
                f = 0
                for jj in range(self.num_dmus):
                    f += z[jj]*y[r][jj]
                lp += f >= y[r][j]

            f = 0
            for jj in range(self.num_dmus):
                f += z[jj]
            lp += f == 1

    def _formulate_output_lp(self):
        y = self.y; u = self.u
        x = self.x; v = self.v
        z = self.z

        # Output increasing  model
        for j, lp in enumerate(self.lp_list):

            # Build objective function
            E = pulp.LpVariable('E', lowBound = 0, 
                    cat = 'Continuous')
            lp += E, 'E'

            # Build constraints
            for i in range(self.num_inputs):
                f = 0
                for jj in range(self.num_dmus):
                    f += x[i][jj]*z[jj]
                lp += f <= x[i][j]

            for r in range(self.num_outputs):
                f = 0
                for jj in range(self.num_dmus):
                    f += z[jj]*y[r][jj]
                lp += f >= E*y[r][j]

            f = 0
            for jj in range(self.num_dmus):
                f += z[jj]
            lp += f == 1

    def _formulate_ccr_lp(self):
        y = self.y; u = self.u
        x = self.x; v = self.v
        z = self.z

        # CCR model
        # Note, the problem needs to be transformed
        # so that it can be solved with an LP
        for j, lp in enumerate(self.lp_list):

            # Build objective function
            E = pulp.LpVariable('E', lowBound = 0, 
                    cat = 'Continuous')
            h = 0
            for r in range(self.num_outputs):
                h += u[r]*y[r][j]
            lp += h, 'h'

            # Build constraints
            for jj in range(self.num_dmus):
                f= 0
                for r in range(self.num_outputs):
                    f += u[r]*y[r][jj]
                for i in range(self.num_inputs):
                    f -= v[i]*x[i][jj]
                lp += f <= 0

            f = 0
            for i in range(self.num_inputs):
                f += v[i]*x[i][j]
            lp += f == 1

    def solve(self):
        eff_scores = []
        for lp in self.lp_list:
            lp.solve()
            eff_scores.append(pulp.value(lp.objective))
        self.eff_scores = eff_scores


            
        

                


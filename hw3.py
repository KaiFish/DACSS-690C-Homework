import pulp as pp
import pandas as pd
	
model = pp.LpProblem(name='vitamin-problem', 
                     sense=pp.LpMinimize)

sv = pp.LpVariable(name="SuperVit",
                 lowBound=0,
                 cat='Integer') #can't buy half a pill

nh = pp.LpVariable(name="NewHealth",
                 lowBound=0,
                 cat='Integer')

svCost = 0.2
nhCost = 0.3
func = svCost*sv + nhCost*nh

C1 = pp.LpConstraint(name='VitaminC',
                    e= 20*sv + 30*nh, 
                    rhs=60,
                    sense=pp.LpConstraintGE)

C2 = pp.LpConstraint(name='Calcium',
                    e= 500*sv + 250*nh, 
                    rhs=1000,
                    sense=pp.LpConstraintGE)

C3 = pp.LpConstraint(name='Iron',
                    e= 9*sv + 2*nh, 
                    rhs=18,
                    sense=pp.LpConstraintGE)

C4 = pp.LpConstraint(name='Niacin',
                    e= 2*sv + 10*nh, 
                    rhs=20,
                    sense=pp.LpConstraintGE)

C5 = pp.LpConstraint(name='Magnesium',
                    e= 60*sv + 90*nh, 
                    rhs=360,
                    sense=pp.LpConstraintGE)

model += func
model += C1
model += C2
model += C3
model += C4
model += C5

model.solve(pp.PULP_CBC_CMD(msg=0))
"Model Status",pp.LpStatus[model.status]

	
Optimal_Decision={"Optimal Solution to minimize cost":pp.value(model.objective)}
Optimal_Decision.update({v.name: v.varValue for v in model.variables()})
print(pd.DataFrame.from_dict(Optimal_Decision,orient='index',columns=['info']).map('{:,.2f}'.format))
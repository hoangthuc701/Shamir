import random
import sys
import numpy as np

class Shamir:
    def extract(self,k, numbers):
        a = np.zeros((k,k+1))
        for i in range(1,k+1):
            for j in range(k,0,-1):
                a[i-1,k-j] = pow(i,j-1)
            a[i-1][k] = numbers[i-1]
        coefficients =  self.gaussSolver(k,a)

        return int(round(coefficients[k-1]))

    def gaussSolver(self, n, matrix):
        a = matrix.astype(float)
        x = np.zeros(n+1)
        for i in range(n):
            if a[i][i] == 0.0:
                sys.exit('Divide by zero detected!')
                
            for j in range(i+1, n):
                ratio = a[j][i]/a[i][i]
                
                for k in range(n+1):
                    a[j][k] = a[j][k] - ratio * a[i][k]

        # Back Substitution
        x[n-1] = a[n-1][n]/a[n-1][n-1]

        for i in range(n-2,-1,-1):
            x[i] = a[i][n]
            
            for j in range(i+1,n):
                x[i] = x[i] - a[i][j]*x[j]
            
            x[i] = x[i]/a[i][i]
        
        return x

    def create(self,s,n,k):
        if k >= n:
            return
        coefficients = [0]*(k-1)
        numbers = [0]
        for i in range(0, k-1):
            value = self.random()
            while value in numbers:
                value = self.random()
            numbers.append(value)
            coefficients[i] = value
        
        coefficients.append(s)

        print(coefficients)
        
        # generate share key
        results = []
        for i in range(1,n+1):
            result = self.evaluate(i,coefficients)
            results.append(result)

        return results

    def evaluate(self,number,coefficients):
        result = 0
        n = len(coefficients) - 1
        for i in range(0, len(coefficients)):
            result = result + coefficients[i]*pow(number,n)
            n = n - 1 
        return result


    def random(self):
        return random.randint(0,10)

shamir = Shamir()
s= 7899
n= 10
k= 9
x = shamir.create(7899,n,k)
print(shamir.extract(k,x)==s)
from openmdao.core.explicitcomponent import ExplicitComponent
import matplotlib.pyplot as plt
import numpy as np
from topfarm.plotting import PlotComp
from topfarm.cost_models.cost_model_wrappers import CostModelComponent


# class DummyCost(ExplicitComponent):
#     """Sum of squared error between current positions and optimal positions
#
#         Evaluates the equation
#         f(x,y) = SUM(x_i - optx_i)^2 + SUM(y_i + opty_i)^2.
#     """
#
#     def __init__(self, optimal_positions):
#         """Pass an Nx2 array (or list of lists) of optimal positions"""
#         ExplicitComponent.__init__(self)
#         self.optimal = np.array(optimal_positions)
#         self.n_wt = self.optimal.shape[0]
#
#     def setup(self):
#         self.add_input('turbineX', val=np.zeros(self.n_wt), units='m')
#         self.add_input('turbineY', val=np.zeros(self.n_wt), units='m')
#         self.add_output('cost', val=0.0)
#         self.declare_partials('cost', '*')
#
#     def compute(self, inputs, outputs):
#         """
#         f(x,y) = SUM(x_i - optx_i)^2 + SUM(y_i + opty_i)^2
#         """
#         x = inputs['turbineX']
#         y = inputs['turbineY']
#         opt_x, opt_y = self.optimal.T[0:2]
#         outputs['cost'] = np.sum((x - opt_x)**2 + (y - opt_y)**2)
#
#     def compute_partials(self, inputs, J):
#         x = inputs['turbineX']
#         y = inputs['turbineY']
#         J['cost', 'turbineX'] = (2 * x - 2 * np.array(self.optimal)[:, 0])
#         J['cost', 'turbineY'] = (2 * y - 2 * np.array(self.optimal)[:, 1])


class DummyCost(CostModelComponent):
    """Sum of squared error between current and optimal state
       Evaluates the equation
       f(x,..) = SUM((x_i - optx_i)^2 + ...).
    """

    def __init__(self, optimal_state, inputs=['turbineX', 'turbineY', 'turbineZ'],
                 input_units={'turbineX': 'm', 'turbineY': 'm', 'turbineZ': 'm'}):
        """
        Parameters
        ----------
        optimal_state : array_like, dim=(#wt,#inputs)
            optimal state array
        inputs : array_like
            list of input names
        """
        self.optimal_state = np.array(optimal_state)
        self.n_wt = self.optimal_state.shape[0]

        CostModelComponent.__init__(self, inputs, self.n_wt, self.cost, self.grad,
                                    input_units)

    def cost(self, **kwargs):
        opt = self.optimal_state
        return np.sum([(kwargs[n] - opt[:, i])**2 for i, n in enumerate(self.input_keys)])

    def grad(self, **kwargs):
        opt = self.optimal_state
        return [(2 * kwargs[n] - 2 * opt[:, i]) for i, n in enumerate(self.input_keys)]


class TurbineTypeDummyCost(DummyCost):
    def __init__(self, optimal):
        if len(np.array(optimal).shape) == 1:
            optimal = np.array([optimal]).T
        DummyCost.__init__(self, optimal, inputs=['turbineType'])


class DummyCostPlotComp(PlotComp):
    def __init__(self, optimal, memory=10, delay=0.001):
        super().__init__(memory, delay)
        self.optimal = optimal

    def init_plot(self, boundary):
        PlotComp.init_plot(self, boundary)
        opt_x, opt_y = np.array(self.optimal).T[0:2]
        for c, optx, opty in zip(self.colors, opt_x, opt_y):
            plt.plot(optx, opty, 'ko', ms=10)
            plt.plot(optx, opty, 'o', color=c, ms=8)


def try_me():
    if __name__ == '__main__':
        from topfarm import TopFarm
        n_wt = 4
        random_offset = 5
        optimal = [(3, -3), (7, -7), (4, -3), (3, -7), (-3, -3), (-7, -7), (-4, -3), (-3, -7)][:n_wt]
        rotorDiameter = 1.0
        minSpacing = 2.0

        turbines = np.array(optimal) + np.random.randint(-random_offset, random_offset, (n_wt, 2))
        plot_comp = DummyCostPlotComp(optimal)

        boundary = [(0, 0), (6, 0), (6, -10), (0, -10)]

        tf = TopFarm(turbines, DummyCost(optimal,['turbineX','turbineY']), minSpacing * rotorDiameter, boundary=boundary, plot_comp=plot_comp, record_id=None)
        # tf.check()
        tf.optimize()
        # plot_comp.show()


try_me()

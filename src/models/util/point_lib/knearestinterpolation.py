import numpy as np
import math
import scipy.io as sio
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error as mae

from .util.base import Base


class KInterpolation(Base):
    def __init__(self, u_obs, u, k=5, constant=298):
        super().__init__(u_obs, u)
        self.k = k

    def knearest(self, row, col):
        d = np.zeros_like(self.rows)
        for k in range(self.rows.shape[0]):
            d[k] = math.sqrt(
                math.pow((self.rows[k] - row), 2) + math.pow((self.cols[k] - col), 2)
            )
        kpoint = np.argsort(d)[: self.k]
        return self.rows[kpoint], self.cols[kpoint]

    def predict(self):

        row = np.linspace(0, self.u.shape[0] - 1, num=self.u.shape[0])
        col = np.linspace(0, self.u.shape[0] - 1, num=self.u.shape[0])
        col, row = np.meshgrid(col, row)

        col = col.reshape(1, -1)
        row = row.reshape(1, -1)

        col = np.dot(np.ones_like(self.cols).reshape(-1, 1), col)
        row = np.dot(np.ones_like(self.rows).reshape(-1, 1), row)

        ksort = np.argsort(
            np.sqrt(
                np.power((self.rows.reshape(-1, 1) - row), 2)
                + np.power((self.cols.reshape(-1, 1) - col), 2)
            ),
            axis=0,
        )

        kind = np.zeros_like(ksort)

        for num in range(ksort.shape[1]):
            kind[ksort[: self.k, num], num] = 1

        assert self.k >= 1

        ind = np.dot(
            np.ones_like(self.rows).reshape(1, -1),
            np.exp(
                -np.sqrt(
                    np.power((self.rows.reshape(-1, 1) - row), 2)
                    + np.power((self.cols.reshape(-1, 1) - col), 2)
                )
            )
            * kind,
        )

        param = (
            np.exp(
                -np.sqrt(
                    np.power((self.rows.reshape(-1, 1) - row), 2)
                    + np.power((self.cols.reshape(-1, 1) - col), 2)
                )
            )
            * kind
            / (np.dot(np.ones_like(self.rows).reshape(-1, 1), ind))
        )

        dis = np.dot(self.u_obs[self.rows, self.cols].reshape(1, -1), param)
        self.u_pred = dis.reshape(self.u.shape[0], self.u.shape[1])

        return self.u_pred


if __name__ == "__main__":
    m = sio.loadmat("Example0.mat")
    u_obs = m["u_obs"]
    u = m["u"]
    sample = KInterpolation(u_obs, u, k=4)
    u_pred = sample.predict()
    print("mae:", mae(u_pred, u))

    fig = plt.figure(figsize=(22.5, 5))

    grid_x = np.linspace(0, 0.1, num=200)
    grid_y = np.linspace(0, 0.1, num=200)
    X, Y = np.meshgrid(grid_x, grid_y)

    fig = plt.figure(figsize=(22.5, 5))

    plt.subplot(141)
    plt.title("Absolute Error")
    im = plt.pcolormesh(X, Y, abs(u - u_pred))
    plt.colorbar(im)
    fig.tight_layout(pad=2.0, w_pad=3.0, h_pad=2.0)

    plt.subplot(142)
    plt.title("Real Temperature Field")
    im = plt.contourf(X, Y, u, levels=150, cmap="jet")
    plt.colorbar(im)

    plt.subplot(143)
    plt.title("Reconstructed Temperature Field")
    im = plt.contourf(X, Y, u_pred, levels=150, cmap="jet")
    plt.colorbar(im)

    plt.subplot(144)
    plt.title("Absolute Error")
    im = plt.contourf(X, Y, abs(u - u_pred), levels=150, cmap="jet")
    plt.colorbar(im)

    # save_name = os.path.join('outputs/predict_plot', '1.png')
    # fig.savefig(save_name, dpi=300)

    # fig = plt.figure(figsize=(5,5))
    # im = plt.imshow(u,cmap='jet')
    # plt.colorbar(im)
    fig.savefig("prediction.png", dpi=300)

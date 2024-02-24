from enum import Enum
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.animation as animation


class Side(Enum):
    BID = 1
    ASK = 2


class PriceLadder:
    min_increment = 0.00001
    base_half_spread = 3 * min_increment
    skew_factor = 1 * min_increment

    def calc(x, half_spread, pos: float):
        def px(side: Side) -> float:
            MID = 0.0
            def px_1() -> float:
                y = - 0.0000000000001 * x**8 + 0.0000000000175 * x**7 - 0.0000000008594 * x**6 + 0.0000000223001 * x**5 \
                    - 0.0000003291554 * x**4 + 0.0000027520073 * x**3 - 0.0000118604919 * x**2 + 0.0000216921451 * x
                return y
            def px_2() -> float:
                y = - 0.00000000000015 * x**8 + 0.00000000001854 * x**7 - 0.00000000093137 * x**6 + 0.00000002458305 * x**5 \
                    - 0.00000036604094 * x**4 + 0.00000304957510 * x**3 - 0.00001277979671 * x**2 + 0.00002077498199 * x
                return y
            # calculate price for bucket
            y = px_2()
            # apply spread
            if side == Side.ASK:
                y += PriceLadder.base_half_spread
            else:
                y *= -1.0
                y -= PriceLadder.base_half_spread
            # shift to mid
            y += MID
            # apply skew
            y -= pos * PriceLadder.skew_factor
            return y

        # get raw skewed prices based on position
        bid, ask = px(Side.BID), px(Side.ASK)

        # redistribute skew s.t.:
        # - you prices do not cross mid; and
        # - the spread for that bucket is maintained
        if ask < PriceLadder.base_half_spread:
            ask = PriceLadder.base_half_spread
            bid = - 2* half_spread + PriceLadder.base_half_spread
        if bid > - PriceLadder.base_half_spread:
            bid = - PriceLadder.base_half_spread
            ask = + 2* half_spread - PriceLadder.base_half_spread
        return bid, ask

    def __init__(self):
        buckets = (1, 2, 3, 4, 5, 6, 7.75, 10, 13, 17, 21.5, 27)
        self.fig, self.ax = plt.subplots()
        self.frames = []
        self._init_plot()
        # create df with zeros
        feature_list = ["bucket", "half_spread", "bid_px", "ask_px"]
        self.df = pd.DataFrame(0, index=np.arange(len(buckets)), columns=feature_list)
        self.df["bucket"] = buckets
        self._calc_ladder(0)
        self.df["half_spread"] = (self.df["ask_px"] - self.df["bid_px"]) / 2.0
        pass

    def _init_plot(self):
        # shift x-axis to middle. clean other axis
        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['right'].set_color('none')
        self.ax.spines['top'].set_color('none')

        # Remove ticks, add labels
        self.ax.xaxis.set_ticks([]), self.ax.set_xlabel("bucket", loc='right')
        # plt.yticks([]), ax.set_ylabel('Price', loc='top')
        self.ax.yaxis.set_ticks([]), self.ax.set_ylabel('Mid', loc='center')

        # set plot size etc
        self.fig.tight_layout()
        self.fig.set_size_inches(12.0, 8.5, forward=True)
        self.fig.set_dpi(120)

    def set_position(self, pos: float):
        self._calc_ladder(pos)
        self._add_plot()
        pass

    def _calc_ladder(self, pos: float) -> None:
        self.df["bid_px"], self.df["ask_px"] = zip(*self.df.apply(lambda x: PriceLadder.calc(x["bucket"], x["half_spread"], pos), axis=1))
        # TODO - check ladder integrity

    def _add_plot(self):
        #print(self.df)

        # plot the lines in the same plot so we can save it for animation
        linewidth = 8
        x = self.df["bucket"]
        pix = self.ax.plot(
            x, self.df["ask_px"], 'r',
            x, self.df["bid_px"], 'b',
            linewidth=linewidth, path_effects=[pe.Stroke(linewidth=linewidth+2, foreground='k'), pe.Normal()])

        self.frames.append(pix)


def main():
    print("Hello")
    ladder = PriceLadder()
    for theta in range(0, 20, 1):
        theta /= 10.0
        theta *= np.pi
        pos = 25 * np.sin(theta)
        ladder.set_position(pos)
    anim = animation.ArtistAnimation(fig=ladder.fig, artists=ladder.frames, interval=250)
    writer = animation.PillowWriter()
    anim.save(filename="pillow_example.gif", writer=writer, dpi=120, savefig_kwargs={"transparent": True})
    #writer = animation.FFMpegWriter()
    #anim.save(filename="pillow_example.mp4", writer=writer, savefig_kwargs={"transparent": True})
    #plt.show()


if __name__ == "__main__":
    main()

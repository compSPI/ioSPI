import numpy as np
from ioSPI import transfer


def test_ctf_freqs():
    N = (np.random.randint(low=8, high=128) // 2) * 2
    freq_1d = transfer.ctf_freqs(N, d=1)
    assert freq_1d.shape == (N // 2,)
    assert np.isclose(freq_1d.min(), 0)
    assert np.isclose(freq_1d[0], 0)
    assert freq_1d[-1] < N // 2
    psize = np.random.uniform(low=1, high=10)
    freq_A_2d, angles_rad = transfer.ctf_freqs(N, d=2, psize=psize)
    assert np.isclose(freq_A_2d[N // 2, 0], 0.5 * psize)
    assert np.isclose(freq_A_2d[N // 2, N // 2], 0)  # dc
    assert freq_A_2d.shape == angles_rad.shape == (N, N)
    assert (-np.pi <= angles_rad.min()) and (angles_rad.max() <= np.pi)


def test_eval_ctf():
    N = (np.random.randint(low=8, high=128) // 2) * 2
    freq_A_2d, angles_rad = transfer.ctf_freqs(N, d=2)
    ac = np.random.uniform(low=0.07, high=0.1)
    ctf = transfer.eval_ctf(
        s=freq_A_2d,
        a=angles_rad,
        def1=1e4,
        def2=1.1e4,
        angast=0,
        phase=0,
        kv=300,
        ac=ac,
        cs=2.0,
        bf=0,
        lp=0,
    )
    assert ctf.shape == (N, N)
    assert np.isclose(ctf[N // 2, N // 2], ac)
    assert -1 <= ctf.min() and ctf.max() <= 1


def test_random_ctfs():
    N = (np.random.randint(low=8, high=128) // 2) * 2
    n_particles = np.random.randint(low=3, high=7)
    df_min = np.random.uniform(low=5000, high=30000)
    df_max = df_min + 100
    df_diff_min = np.random.uniform(low=1, high=100)
    df_diff_max = df_diff_min + 100
    df_ang_min = np.random.uniform(low=0, high=360)
    df_ang_max = np.random.uniform(low=df_ang_min, high=360)
    ctfs, df1s, df2s, df_ang_deg = transfer.random_ctfs(
        N,
        psize=1,
        n_particles=n_particles,
        df_min=df_min,
        df_max=df_max,
        df_diff_min=df_diff_min,
        df_diff_max=df_diff_max,
        df_ang_min=df_ang_min,
        df_ang_max=df_ang_max,
        kv=300,
        ac=0.1,
        cs=2.0,
        phase=0,
        bf=0,
        do_log=False,
    )
    assert ctfs.shape == (n_particles, N, N)
    assert df_min - df_diff_max <= df1s.min()
    assert df1s.max() <= df_max + df_diff_max
    assert df_ang_min <= df_ang_deg.min() and df_ang_deg.max() <= df_ang_max

import java.util.concurrent.RecursiveAction;

public class FireTask extends RecursiveAction {

    // row indices
    private final int lo;
    private final int hi;

    // cutoff
    private final int cutoff;

    // terrain map
    private FireMapParallel map;

    public FireTask(FireMapParallel map, int lo, int hi, int cutoff) {
        this.lo = lo;
        this.hi = hi;
        this.cutoff = cutoff;
        this.map = map;
    }

    protected void compute() {

        if (hi - lo < cutoff) {

            for (int i = lo; i <= hi; i++) {

                for (int j = 0; j < map.getColumns(); j++) {

                    // do calculation for the cell at this index

                }

            }

        }

        int mid = (lo + hi) / 2;
        FireTask left = new FireTask(map, lo, mid, cutoff);
        FireTask right = new FireTask(map, mid + 1, hi, cutoff);

        left.fork();
        right.compute();
        left.join();

    }

}

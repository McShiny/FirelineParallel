import java.util.concurrent.RecursiveTask;

public class FireTask extends RecursiveTask<FireMap.StepResult> {

    // row indices
    private final int lo;
    private final int hi;

    // cutoff
    private final int cutoff;

    // terrain map
    private FireMapParallel map;

    // mode
    private final FireMap.Mode mode;

    public FireTask(FireMapParallel map, int lo, int hi, int cutoff, FireMap.Mode mode) {
        this.lo = lo;
        this.hi = hi;
        this.cutoff = cutoff;
        this.map = map;
        this.mode = mode;
    }

    @Override
    protected FireMap.StepResult compute() {

        if (hi - lo < cutoff) {

            return map.updateRegion(mode, lo, hi, 1, map.getColumns() - 1);

        }

        int mid = (lo + hi) / 2;
        FireTask left = new FireTask(map, lo, mid, cutoff, mode);
        FireTask right = new FireTask(map, mid, hi, cutoff, mode);

        left.fork();
        FireMap.StepResult right_result = right.compute();
        FireMap.StepResult left_result = left.join();

        return FireMap.StepResult.combine(left_result, right_result);

    }

}

import java.util.concurrent.ForkJoinPool;

public class FireMapParallel extends FireMap {

    private ForkJoinPool pool;
    private int sequentialCutoff;

    public FireMapParallel(int rows, int columns, long seed, Mode mode, ForkJoinPool pool) {
        super(rows, columns, seed, mode);
        this.pool = pool;
    }

    public FireMapParallel(int rows,
            int columns,
            long seed,
            Mode mode,
            ForkJoinPool pool,
            Landscape landscape,
            Integer ignitionTopRow,
            Integer ignitionLeftColumn,
            Integer ignitionPatchSize) {
        super(rows, columns, seed, mode, landscape,
                ignitionTopRow, ignitionLeftColumn, ignitionPatchSize);
        this.pool = pool;
    }

    public StepResult stepParallel(Mode mode, ForkJoinPool pool, int cutoff) {
        prepareNextState();
        FireTask root = new FireTask(this, 1, getRows() - 1, cutoff, mode);
        pool.execute(root);
        StepResult result = root.join();
        completeStep();
        return result;
    }

}

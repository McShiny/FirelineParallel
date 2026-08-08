import java.util.concurrent.ForkJoinPool;

public class FireMapParallel extends FireMap {

    private ForkJoinPool pool;
    private int sequentialCutoff;

    public FireMapParallel(int rows, int columns, long seed, Mode mode, ForkJoinPool pool, int sequentialCutoff) {
        super(rows, columns, seed, mode);
        this.sequentialCutoff = sequentialCutoff;
        this.pool = pool;
    }

    public FireMapParallel(int rows,
            int columns,
            long seed,
            Mode mode,
            ForkJoinPool pool,
            int sequentialCutoff,
            Landscape landscape,
            Integer ignitionTopRow,
            Integer ignitionLeftColumn,
            Integer ignitionPatchSize) {
        super(rows, columns, seed, mode, landscape,
                ignitionTopRow, ignitionLeftColumn, ignitionPatchSize);
        this.sequentialCutoff = sequentialCutoff;
        this.pool = pool;
    }

    public StepResult stepParallel(Mode mode, ForkJoinPool pool, int cutoff) {
        prepareNextState();
        FireTask root = new FireTask(this, 0, getRows(), sequentialCutoff);
        root.fork();
        root.join();
        // assign some result
        completeStep();
        // return result
    }

}

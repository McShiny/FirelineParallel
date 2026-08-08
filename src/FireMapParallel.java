public class FireMapParallel extends FireMap {

    public FireMapParallel(int rows, int columns, long seed, Mode mode) {
        super(rows, columns, seed, mode);
    }

    public FireMapParallel(int rows,
            int columns,
            long seed,
            Mode mode,
            Landscape landscape,
            Integer ignitionTopRow,
            Integer ignitionLeftColumn,
            Integer ignitionPatchSize) {
        super(rows, columns, seed, mode, landscape,
                ignitionTopRow, ignitionLeftColumn, ignitionPatchSize);
    }
}

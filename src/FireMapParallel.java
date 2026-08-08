import java.awt.Color;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.Random;
import java.util.concurrent.ForkJoinPool;

import javax.imageio.ImageIO;

public class FireMapParallel extends FireMap {

    private int sequentialCutoff;

    public FireMapParallel(int rows, int columns, long seed, Mode mode, int sequentialCutoff) {
        super(rows, columns, seed, mode);
        this.sequentialCutoff = sequentialCutoff;
    }

    public FireMapParallel(int rows,
            int columns,
            long seed,
            Mode mode,
            int sequentialCutoff,
            Landscape landscape,
            Integer ignitionTopRow,
            Integer ignitionLeftColumn,
            Integer ignitionPatchSize) {
        super(rows, columns, seed, mode, landscape,
                ignitionTopRow, ignitionLeftColumn, ignitionPatchSize);
        this.sequentialCutoff = sequentialCutoff;
    }

    public StepResult stepParallel(Mode mode, ForkJoinPool pool, int cutoff) {
        prepareNextState();
    }

}

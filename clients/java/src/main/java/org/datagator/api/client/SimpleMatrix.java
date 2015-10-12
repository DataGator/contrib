/*
 * Copyright 2015 University of Denver <http://pardee.du.edu/>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.datagator.api.client;

import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;

/**
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/09/07
 */
@JsonDeserialize(using = MatrixDeserializer.class)
public class SimpleMatrix
        extends Entity
        implements Matrix {

    public static SimpleMatrix create(Reader reader)
            throws IOException {
        return (SimpleMatrix) Entity.create(reader);
    }

    private final int rowsCount;
    private final int columnsCount;
    private final Object[][] rows;
    private final int bodyRow;
    private final int bodyColumn;

    protected SimpleMatrix(int columnHeaders, int rowHeaders, Object[][] rows,
            int rowsCount, int columnsCount) {
        super("datagator#Matrix");
        this.bodyRow = columnHeaders;
        this.bodyColumn = rowHeaders;
        this.rows = rows;
        this.rowsCount = rowsCount;
        this.columnsCount = columnsCount;
    }

    @Override
    public int getRowsCount() {
        return rowsCount;
    }

    @Override
    public int getColumnsCount() {
        return columnsCount;
    }

    @Override
    public Matrix getColumnHeaders() {
        Object[][] slice = new Object[bodyRow][];
        for (int r = 0; r < bodyRow; r++) {
            slice[r] = rows[r];
        }
        return new SimpleMatrix(0, bodyColumn, slice, bodyRow, columnsCount);
    }

    @Override
    public Object[][] toArray() {
        return rows;
    }

    public static void main(String[] args)
            throws IOException {
        FileReader reader
                = new FileReader("../../data/json/IGO_Weighted_Dyad.json");
        SimpleMatrix matrix = (SimpleMatrix) Entity.create(reader);

        // empty matrix
        //Matrix matrix = (SimpleMatrix) Entity.create(new java.io.StringReader(
        //    "{\"kind\": \"datagator#SimpleMatrix\", \"columnHeaders\": 0, " +
        //    "\"rowHeaders\": 0, \"rows\": [[]], \"rowsCount\": 1, " +
        //    "\"columnsCount\": 0}"));
        System.out.println(matrix.kind);
        System.out.println(Integer.toString(matrix.rowsCount));
        System.out.println(Integer.toString(matrix.columnsCount));
    }
}

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
package org.datagator.tools.importer.impl;

import java.io.IOException;
import java.io.InputStream;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.poi.hssf.eventusermodel.HSSFEventFactory;
import org.apache.poi.hssf.eventusermodel.HSSFListener;
import org.apache.poi.hssf.eventusermodel.HSSFRequest;
import org.apache.poi.hssf.eventusermodel.MissingRecordAwareHSSFListener;
import org.apache.poi.hssf.record.BOFRecord;
import org.apache.poi.hssf.record.BoundSheetRecord;
import org.apache.poi.hssf.record.LabelSSTRecord;
import org.apache.poi.hssf.record.NumberRecord;
import org.apache.poi.hssf.record.Record;
import org.apache.poi.hssf.record.RowRecord;
import org.apache.poi.hssf.record.SSTRecord;
import org.datagator.tools.importer.AtomType;
import org.datagator.tools.importer.InputStreamExtractor;

/**
 * Extract data from XLSX (Excel 2007 OOXML) input stream.
 *
 * @author N/A
 * @date 2015/10/13
 */
public class XlsxInputStreamExtractor extends InputStreamExtractor {

    private static class EventTransformer
            implements HSSFListener {

        private final BlockingQueue<ImmutablePair<AtomType, Object>> _queue;

        EventTransformer(BlockingQueue<ImmutablePair<AtomType, Object>> queue) {
            _queue = queue;
        }

        @Override
        public void processRecord(Record record) {
            switch (record.getSid()) {
                case BOFRecord.sid:
                    // start of sheet or workbook
                    BOFRecord bof = (BOFRecord) record;
                    // TODO
                    break;
                case BoundSheetRecord.sid:
                    // start of worksheet
                    BoundSheetRecord bsr = (BoundSheetRecord) record;
                    // TODO
                    break;
                case RowRecord.sid:
                    RowRecord rowrec = (RowRecord) record;
                    // TODO
                    break;
                case NumberRecord.sid:
                    NumberRecord numrec = (NumberRecord) record;
                    // TODO
                    break;
                // SSTRecords store a array of unique strings used in Excel.
                case SSTRecord.sid:
                    SSTRecord sstrec = (SSTRecord) record;
                    // TODO
                    break;
                case LabelSSTRecord.sid:
                    LabelSSTRecord lrec = (LabelSSTRecord) record;
                    // TODO
                    break;
                case -1:
                    // MissingRowDummyRecord
                    // MissingCellDummyRecord
                    // LastCellOfRowDummyRecord
                    // TODO
                    break;
            }
        }
    }

    public static final int MAX_QUEUE_CAPACITY = 1024;
    private final BlockingQueue<ImmutablePair<AtomType, Object>> _queue;

    public XlsxInputStreamExtractor(InputStream stream) throws IOException {
        super(stream);
        _queue = new ArrayBlockingQueue<ImmutablePair<AtomType, Object>>(MAX_QUEUE_CAPACITY);
        final HSSFRequest request = new HSSFRequest();
        request.addListenerForAllRecords(new MissingRecordAwareHSSFListener(
                new EventTransformer(_queue)));
        final HSSFEventFactory factory = new HSSFEventFactory();
        factory.processEvents(request, stream);
    }

    @Override
    public AtomType nextAtom() throws IOException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public AtomType getCurrentAtomType() {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public Object getCurrentAtomData() {
        throw new UnsupportedOperationException("Not supported yet.");
    }

}

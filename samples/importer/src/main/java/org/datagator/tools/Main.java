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
package org.datagator.tools;

import java.io.IOException;

/**
 * CLI Interface of DataGator Tools.
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/10/02
 */
public class Main {
    public static void main(String[] args) throws IOException {
        org.datagator.tools.importer.Main.main(args);
    }
}

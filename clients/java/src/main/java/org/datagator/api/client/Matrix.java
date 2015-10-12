package org.datagator.api.client;

/**
 * Four-square model of Matrix object
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/09/03
 */
public interface Matrix
{
    public int getRowsCount();
    public int getColumnsCount();
    public Matrix getColumnHeaders();
    public Object[][] toArray();
}

sqlalchemy = {
    'sql_connection' : 'mysql://stack:password@localhost/lbaas?charset=utf8&use_unicode=0',
    'db_auto_create' : True,
    'sql_retry_interval' : 1,
    'sql_max_retries' : 2,
    'sql_idle_timeout' : 3600,
    'max_limit_paging' : 100,
    'default_limit_paging' : 10,
    'debug': True
}
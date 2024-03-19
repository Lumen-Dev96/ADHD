{application,mnesia_rocksdb,
             [{description,"RocksDB backend plugin for Mnesia"},
              {vsn,"0.1.15"},
              {modules,[mnesia_rocksdb,mnesia_rocksdb_app,mnesia_rocksdb_lib,
                        mnesia_rocksdb_params,mnesia_rocksdb_sup,
                        mnesia_rocksdb_tuning]},
              {registered,[]},
              {mod,{mnesia_rocksdb_app,[]}},
              {env,[]},
              {applications,[kernel,stdlib,rocksdb,sext]}]}.
{application,emqx_ctl,
             [{description,"Backend for emqx_ctl script"},
              {vsn,"0.1.6"},
              {registered,[]},
              {mod,{emqx_ctl_app,[]}},
              {applications,[kernel,stdlib]},
              {env,[]},
              {modules,[emqx_ctl,emqx_ctl_app,emqx_ctl_sup]},
              {licenses,["Apache-2.0"]},
              {links,[]}]}.
        function loadSelectedObjects(stub_object) {
           if (stub_object['type'] == 'roa') {
               webix.ajax("/api/objects/roa/"+stub_object['filename'],{
                   error:function(text, data, XmlHttpRequest){
                      alert(text);
                   },
                   success:function(text, data, XmlHttpRequest){
                      var stuff = data.json();
                      $$("roa_properties").setValues(stuff);
                      var roa_table = $$("roa_table");
                      roa_table.clearAll();
                      var index = 0;
                      stuff['prefixes'].forEach(function(pref) {
                         var res = pref.split("_");
                         roa_table.add({id:index, prefix: res[0], max_length: res[1]}); 
                      });
                      $$("object_properties_layout").showBatch("roa_batch");
                   }
               }); 

               webix.ajax("/api/objects/roa_rc/" + stub_object['filename'], {
               	error:function(text, data, XmlHttpRequest) {
               		alert(text);
               	},
               	success:function(text, data, XmlHttpRequest) {
               		var content = data.json();
                    content['width'] = 500;
                    var resource_list = $$("ee_cer_resource_list");
                    resource_list.clearAll();
                    var index = 0;
                    if (content['asn_ranges'] != "None") {
                    	content['asn_ranges'].forEach(function(range) {
                        	resource_list.add({id:index, resource: "AS" + range['lower'] + " - AS" + range['upper']});
                        	index++;
                      	});
                    }

                    if (content['asns'] != "None") {
                    	content['asns'].forEach(function(asn) {
                        	resource_list.add({id:index, resource: "AS"+asn});
                        	index++;
                        });
                    }

                    if (content['prefixes'] != "None") {
                    	content['prefixes'].forEach(function(prefix) {
                        	resource_list.add({id:index, resource: prefix});
                        	index++;
                        });
                    }
                    $$("ee_cer_properties").setValues(content);
               	}
               })
           }
           if (stub_object['type'] == 'cer') {
               var mft_filename = stub_object['mft_name'];
               var crl_filename = stub_object['crl_name'];
               webix.ajax("/api/objects/rc/"+ stub_object['filename'],{
                   error:function(text, data, XmlHttpRequest){
                       alert(text);
                   },
                   success:function(text, data, XmlHttpRequest){
                      var stuff = data.json();
                      stuff['width'] = 500;
                      var resource_list = $$("cer_resource_list");
                      resource_list.clearAll();
                      var index = 0;
                      if (stuff['asn_ranges'] != "None") {
                        stuff['asn_ranges'].forEach(function(range) {
                          resource_list.add({id:index, resource: "AS" + range['lower'] + " - AS" + range['upper']});
                          index++;
                        });
                      }

                      if (stuff['asns'] != "None") {
                        stuff['asns'].forEach(function(asn) {
                          resource_list.add({id:index, resource: "AS"+asn});
                          index++;
                        });
                      }

                      if (stuff['prefixes'] != "None") {
                        stuff['prefixes'].forEach(function(prefix) {
                          resource_list.add({id:index, resource: prefix});
                          index++;
                        });
                      }


                      $$("cer_properties").setValues(stuff);
                      $$("object_properties_layout").showBatch("cer_batch");
                   }
               }); 
               webix.ajax("/api/objects/mft/"+mft_filename,{
                   error:function(text, data, XmlHttpRequest){
                      alert(text);
                   },
                   success:function(text, data, XmlHttpRequest){
                      var stuff = data.json();
                      $$("mft_properties").setValues(stuff);
                      var mft_table = $$("manifest_table");
                      mft_table.clearAll();
                      var index = 0 ;
                      stuff['files'].forEach(function(entry) {
                        var res = entry.split(" ");
                        mft_table.add({id:index, filename: res[0], hash: res[1]});
                      });
                   }
               }); 
               webix.ajax("/api/objects/crl/"+crl_filename,{
                   error:function(text, data, XmlHttpRequest){
                      alert(text);
                   },
                   success:function(text, data, XmlHttpRequest){
                      var stuff = data.json();
                      $$("crl_properties").setValues(stuff);
                      var crl_table = $$("crl_table");
                      crl_table.clearAll();
                      var index = 0 ;
                      if (stuff['revoked_objects'] != "None") {
                        stuff['revoked_objects'].forEach(function(entry) {
                          var res = entry.split(" ");
                          crl_table.add({id:index, serial_nr: res[0], revoke_time: res[1]});
                        });
                      }
                   }
               }); 
           }
           
        }

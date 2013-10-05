# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_plugin 'vagrant-omnibus'
Vagrant.require_plugin 'vagrant-berkshelf'

ip_addresses = {
  :tinge       => '192.0.2.2',
  :blend       => '192.0.2.3',
  :spread      => '192.0.2.4',

  :queue       => '192.0.2.5',
  :token_store => '192.0.2.6',
  :datastore   => '192.0.2.7',
}

margarine_attributes = {
  :margarine => {
    :queue => { :hostname => ip_addresses[:queue] },
    :datastore => { :hostname => ip_addresses[:datastore] },
    :token_store => { :hostname => ip_addresses[:token_store] },
    :urls => { 
      :tinge => 'http://#{ip_addresses[:tinge]}',
      :blend => 'http://api.#{ip_addresses[:blend]}/v1/',
    },
  },
}

Vagrant.configure('2') do |config|
  config.vm.box = 'precise64'
  config.vm.box_url = 'http://files.vagrantup.com/precise64.box'

  config.vm.define 'token_store' do |token_store|
    token_store.vm.network :private_network, ip: ip_addresses[:token_store]
        
    token_store.vm.provision 'shell', inline: <<-EOF
      apt-get -q=2 update
      apt-get -q=2 -y install redis-server
      sed -i -e \'s/bind 127.0.0.1/#\0/\' /etc/redis/redis.conf
      service redis-server restart
    EOF
  end

  config.vm.define 'queue' do |queue|
    queue.vm.network :private_network, ip: ip_addresses[:queue]

    queue.omnibus.chef_version = :latest
    queue.vm.provision :chef_solo do |chef|
      chef.node_name = 'queue'

      chef.log_level = :info

      chef.roles_path = 'chef/roles'
      chef.environments_path = 'chef/environments'
      chef.data_bags_path = 'chef/data_bags'

      chef.environment = 'vagrant'
      chef.add_role 'queue'
    end
  end

  config.vm.define 'datastore' do |datastore|
    datastore.vm.network :private_network, ip: ip_addresses[:datastore]
      
    datastore.omnibus.chef_version = :latest
    datastore.vm.provision :chef_solo do |chef|
      chef.node_name = 'datastore'

      chef.log_level = :info

      chef.roles_path = 'chef/roles'
      chef.environments_path = 'chef/environments'
      chef.data_bags_path = 'chef/data_bags'

      chef.environment = 'vagrant'
      chef.add_role 'datastore'
    end
  end

  [ :tinge, :blend, :spread ].each do |component|
    config.vm.define component do |box|
      box.vm.network :private_network, ip: ip_addresses[component]

      box.omnibus.chef_version = :latest
      box.vm.provision :chef_solo do |chef|
        chef.node_name = component

        chef.log_level = :info

        chef.roles_path = 'chef/roles'
        chef.environments_path = 'chef/environments'
        chef.data_bags_path = 'chef/data_bags'

        chef.json = margarine_attributes

        chef.environment = 'vagrant'
        chef.add_role component
      end
    end
  end
end

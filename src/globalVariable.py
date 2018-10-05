
# Check Configuring Flask-Cache section for more details, other type of cache available:
# null: NullCache (default)
# simple: SimpleCache
# memcached: MemcachedCache (pylibmc or memcache required)
# gaememcached: GAEMemcachedCache
# redis: RedisCache (Werkzeug 0.7 required)
# filesystem: FileSystemCache
# saslmemcached: SASLMemcachedCache (pylibmc required)

CACHE_TYPE = 'simple'
timeout_max = 7200
timeout_min = 300


payment_type = 'bank_transfer'
transaction_status = 'RECEIVE'
topup_status_message = 'Order Goldmil Berhasil, Silahkan Melanjutkan Transaksi.'
create_by = '1'
key = "0123456789abcdefghijklmnopqrstuv"
port = 5060
length_pin = 6
prefix_code_order_number = 'ORD'
prefix_code_withdraw_number = 'WD'
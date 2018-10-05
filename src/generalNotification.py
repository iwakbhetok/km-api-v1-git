from flask import Flask, request, jsonify
from flask_restful import Resource, Api

def TokenNotAvailable(self):
    return jsonify({'status ':"error", 'code': 400, "result":"No Token Available"})

def DataNotAvailable(self):
    return jsonify({'status ':"error", 'code': 500, "result":"No Data Available"})
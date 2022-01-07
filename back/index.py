#!/usr/bin/env python3
# coding: utf-8

import datetime
import itertools
import re
import time
from datetime import date

# import mysql.connector
import requests
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import token_filter
from textblob import TextBlob

from db import DB as mysqlDB
from settings import db_elastic, db_extranet
from utils import timeit



class Indexer:
    def __init__(self, name):
        self.name = name
        self.es = Elasticsearch(**db_elastic)
        self.db = mysqlDB()
        # default langs available in DB
        self.langs = {0: "fr", 1: "en"}
        self.updated = None
        self.id = None
        self.vulns = None
        self.infos = None
        self.targets = None
        self.docs = None

    def setup(self):
        """
        Setup the index based on name:
        - Create the index
        - Declare the settings
        - Declare the mappings
        """

        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "std_english": {"type": "standard", "stopwords": "_english_"},
                        "std_french": {
                            "filters": ["standard", "lowercase", "icu_folding"],
                            "type": "custom",
                            "stopwords": "_french_",
                            "tokenizer": "icu_tokenizer",
                        },
                    }
                },
            }
        }
        resp = self.es.indices.create(index=self.name, body=settings, ignore=400)
        print(resp)
        mappings = {
            "properties": {
                # "CVE_id": {
                # "type": "text"
                # },
                # "category_en": {
                # "type": "text"
                # },
                # "category_fr": {
                # "type": "text"
                # },
                "description_en": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}},
                    "analyzer": "std_english",
                },
                "description_fr": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}},
                    "analyzer": "std_french",
                },
                "editor": {"type": "text", "analyzer": "std_english"},
                # "exploit_code_fr": {
                # "type": "text"
                # },
                # "exploitation_in_the_wild": {
                # "type": "integer"
                # },
                # "impact": {
                # "type": "text"
                # },
                # "impact_en": {
                # "type": "text"
                # },
                # "impact_fr": {
                # "type": "text"
                # },
                # "indexed": {
                # "type": "date"
                # },
                # "level": {
                # "type": "integer"
                # },
                # "nessus_id": {
                # "type": "integer"
                # },
                "os_editor": {"type": "text", "analyzer": "std_english"},
                "os_version": {"type": "text", "analyzer": "std_english"},
                "product": {"type": "text", "analyzer": "std_english"},
                "publication": {"type": "date"},
                # "qualys_id": {
                # "type": "text"
                # },
                "reference_en": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}},
                    "analyzer": "std_english",
                },
                "reference_fr": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}},
                    "analyzer": "std_french",
                },
                "solution_en": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}},
                    "analyzer": "std_english",
                },
                "solution_fr": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}},
                    "analyzer": "std_french",
                },
                # "tags_en": {
                # "type": "keyword"
                # },
                # "tags_fr": {
                # "type": "keyword"
                # },
                "title_en": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}},
                    "analyzer": "std_english",
                },
                "title_fr": {
                    "type": "text",
                    "fields": {"raw": {"type": "keyword"}},
                    "analyzer": "std_french",
                },
                # "type_en": {
                # "type": "text"
                # },
                # "type_fr": {
                # "type": "text"
                # },
                "updated": {"type": "date"},
            }
        }
        resp = self.es.indices.put_mapping(index=self.name, body=mappings)
        print(resp)

    @timeit
    def select_vulns(self, id=None, updated=None):
        """ build query for vulns 
        given col_names and tables_names
        execute query and map using key_names
        SELECT from query return list of dict 
        if id is None then multi match
        """
        self.id = id
        self.updated = updated
        # keys of the dict
        key_names = [
            "vuln_id",
            "publication",
            "updated",
            "title_en",
            "exploitcode_fr",
            "exploitation_in_the_wild",
            "last_updated",
            "level",
            # "level_en",
            "category_en",
            "category_fr",
            "type_fr",
            "type_en",
            "impact",
            "impact_en",
            "impact_fr",
            # "current_version",
            "nessus_id",
            "qualys_id",
            "CVE_id",
            "CVSS_base_score",
        ]
        self.vuln = dict.fromkeys(
            key_names, {"type": "", "description": "", "col_name": ""}
        )
        # columns names
        col_names = [
            "vulns.ID",
            "vulns.publication",
            "vulns.updated",
            "vulns.title",
            "vulns.exploit_code",
            "vulns.exploitation_in_the_wild",
            "vulns.last_update",
            "vulns.level",
            # "vulns_level.name",
            "vulns_categories.nom1",
            "vulns_categories.label",
            "vulns_type.nom0",
            "vulns_type.nom1",
            "GROUP_CONCAT(DISTINCT vulns_impacts.impact)",
            "GROUP_CONCAT(DISTINCT vulns_impacts_labels.label_en )",
            "GROUP_CONCAT(DISTINCT vulns_impacts_labels.label)",
            # "MAX(vulns_validation_historic.version)",
            "GROUP_CONCAT(DISTINCT vulns_nessus.nid)",
            "GROUP_CONCAT(DISTINCT vulns_qualys.qid)",
            "GROUP_CONCAT(DISTINCT vulns2cve.cve)",
            "sivm_cvssBaseScore.score",
        ]
        table_names = [
            "vulns",
            "vulns_level  ON vulns_level.level = vulns.level",
            "vulns_categories ON vulns_categories.ID = vulns.cat",
            "vulns_type ON vulns_type.initial = vulns.type",
            "vulns_impacts ON vulns_impacts.vuln = vulns.ID",
            "vulns_impacts_labels ON vulns_impacts_labels.ID = vulns_impacts.impact",
            # "vulns_validation_historic ON vulns_validation_historic.vulns_id = vulns.ID",
            "vulns_nessus ON vulns_nessus.vulns=vulns.ID",
            "vulns_qualys ON vulns_qualys.vulns=vulns.ID",
            "vulns2cve ON vulns2cve.vulns =vulns.ID",
            "sivm_cvssBaseScore ON sivm_cvssBaseScore.vuln_id = vulns.ID",
        ]
        selection = [
            "{} as {}".format(col, key) for col, key in zip(col_names, key_names)
        ]
        values_selection = "SELECT " + ", ".join(selection)
        tables_selection = "FROM " + " LEFT JOIN ".join(table_names)

        query = values_selection + " " + tables_selection
        if self.id is not None and self.updated is not None:
            filter_selection = " WHERE vulns.ID={} AND vulns.updated>='{}'".format(
                self.id, self.updated
            )
            grouping = ";"
        elif self.id is not None and self.updated is None:
            filter_selection = " WHERE vulns.ID={}".format(self.id)
            grouping = ";"
        elif updated is not None and self.id is None:
            filter_selection = " WHERE vulns.updated>='{}'".format(self.updated)
            grouping = "GROUP BY vulns.ID;"
        else:
            filter_selection = " "
            grouping = "GROUP BY vulns.ID;"

        final_query = query + filter_selection + " " + grouping
        
        self.vulns = [self.map_types(dict(zip(key_names, r))) for r in self.db.query(final_query) if r is not None ]
        return self.vulns

    @timeit
    def select_infos(self, id=None, updated=None):
        """ build query for info 
        solution, description as lang fr and en
        reference as lang en and no fr (but content langage seems to be mixed)
        contents are multiple 
        
        description_fr
        description_en
        solution_fr
        solution_en
        reference_fr

        """
        col_names = [
            "vulns_info.vulns",
            "vulns_info.info",
            "vulns_info.lang",
            "group_concat(distinct(vulns_info.text) SEPARATOR ' ')",
            "vulns.updated",
        ]

        key_names = ["vuln_id", "info_type", "lang_code", "contents", "updated_date"]
        # SELECT
        selection = [
            "{} as {}".format(col, key) for col, key in zip(col_names, key_names)
        ]
        values_selection = "SELECT " + ", ".join(selection)
        # FROM
        table_names = ["vulns_info", "vulns ON vulns_info.vulns = vulns.ID"]
        tables_selection = "FROM " + " LEFT JOIN ".join(table_names)
        query = values_selection + " " + tables_selection

        # WHERE
        info_types = ["description", "solution", "reference"]
        flat_params = [(i, l[0], l[1]) for i in info_types for l in self.langs.items()]
        results = []
        # select every vuln_info by type and by lang
        for info_type, lang_code, lang_label in flat_params:
            filters = []
            # additionnal_filter = ' WHERE vulns_info.lang = {} AND vulns_info.info = "{}"'.format(lang_code, info_type)
            filters.append("vulns_info.info='{}'".format(info_type))
            filters.append("vulns_info.lang={}".format(lang_code))
            
            if updated is not None and id is not None:
                filters.append("vulns.updated>='{}'".format(updated))
                filters.append("vulns.ID={}".format(id))
                sorting = " "
                grouping = " "

            elif updated is not None and id is None:
                filters.append("vulns.updated>='{}'".format(updated))
                sorting = " ORDER BY vulns_info.date DESC"
                grouping = " GROUP BY vulns.ID "

            elif id is not None and updated is None:
                filters.append("vulns.ID={}".format(id))
                sorting = " "
                grouping = " "
            else:
                sorting = " ORDER BY vulns_info.date DESC"
                grouping = " GROUP BY vulns.ID "
            filter_selection = " WHERE " + " AND ".join(filters)
            final_query = query + filter_selection + grouping + sorting + ";"
            new_key_names = ["vuln_id",info_type+"_"+lang_label, 'updated']
            # we collect only vuln_id, contents, updated 
            results.extend([
                dict(zip(new_key_names,(n[0], re.sub(r"\n|\t|\r", " ", n[-2]), n[-1])))
                for n in self.db.query(final_query)
                if n[0] is not None
            ])
        # initially results are grouped by contents_type and lang
        # so we will group by vuln_id and merge into same dict
        # to get the full content for 1 vuln_id
        results = list(sorted(results, key=lambda x: x["vuln_id"]))
        self.infos = []
        for vuln_id, grouped_vuln in itertools.groupby(results,key=lambda x: x["vuln_id"]):
            new_dict = {"vuln_id": vuln_id}
            for l in list(grouped_vuln):
                new_dict.update(l)
            self.infos.append(new_dict)
        return self.infos

    @timeit
    def select_products(self):
        tables_names = [
            "vulns_versions",
            "vulns_products ON vulns_products.id = vulns_versions.product",
            "vulns_vendors ON vulns_vendors.id = vulns_products.vendor",
            # "vulns ON vulns.ID = sivm_calcVulnsTargets.vuln_id"
        ]

        key_names = [
            "editor_id",
            "editor_name",
            "product_id",
            "product_name",
            "os",
            "supervise_versions",
            "version_id",
            "version_name",
        ]
        col_names = [
            "vulns_vendors.id",
            "vulns_vendors.label",
            "vulns_products.id",
            "vulns_products.label",
            "vulns_products.os_flag",
            "vulns_products.supervise_versions",
            "vulns_versions.id",
            "vulns_versions.label",
        ]
        # SELECT
        selection = [
            " {} as {} ".format(col, key) for col, key in zip(col_names, key_names)
        ]
        values_selection = "SELECT DISTINCT " + ",".join(selection)
        # FROM
        if len(tables_names) > 1:
            tables_selection = "FROM " + " LEFT JOIN ".join(tables_names)
        else:
            tables_selection = "FROM " + tables_names[0]

        query = values_selection + " " + tables_selection
        filters = []
        # WHERE
        filters.append("vulns_vendors.id != 1")
        sorting = (
            " ORDER BY vulns_vendors.label, vulns_products.label, vulns_versions.label;"
        )
        grouping = ""
        if len(filter_selection) > 1:
            filter_selection = " WHERE " + " AND ".join(filters)
        else:
            filter_selection = " WHERE " + filters[0]

        final_query = query + filter_selection + sorting
        return [dict(zip(key_names, r)) for r in self.db.query(final_query) if r is not None]
    @timeit
    def select_targets(self, id=None, updated=None):
        # ALIASING
        key_names = [
            "editor_id",
            "editor",
            "product_id",
            "product",
            "os_editor_id",
            "os_editor",
            "os_version_id",
            "os_version",
            # "temporal_score",
            # "base_score",
            # "temporal_vector",
            "vuln_id",
            "updated",
            "publication",
        ]
        col_names = [
            "product.vendorId",
            "product.vendorLabel",
            "product.productId",
            "product.productLabel",
            "os.vendorId",
            "os.vendorLabel",
            "os.version_id",
            "os.versionLabel",
            # "target.TScore",
            # "target.BScore",
            # "target.cvssSubVect",
            "target.vulns_id",
            "vulns.updated",
            "vulns.publication",
        ]
        table_names = [
            "sivm_calcVulnsTargets",
            "sivm_calcProductVersions",
            "sivm_calcProductVersions",
            "vulns",
        ]
        table_labels = ["target", "product", "os", "vulns"]
        joins = [
            "target.product_version=product.version_id",
            "target.os_version=os.version_id",
            "vulns.ID=target.vulns_id",
        ]
        # SELECT
        col_mapping = [
            "{} as {}".format(name, label) for name, label in zip(col_names, key_names)
        ]
        value_selection = "SELECT distinct " + " , ".join(col_mapping)
        # FROM
        table_mapping = [
            "{} as {} ".format(name, label)
            for name, label in zip(table_names, table_labels)
        ]
        table_joints = "".join(
            [
                " INNER JOIN {} ON {} ".format(t_label, join)
                for t_label, join in zip(table_mapping[1:], joins)
            ]
        )
        table_selection = "FROM {}".format(table_mapping[0]) + table_joints

        # WHERE
        if id is not None and updated is not None:
            filter_selection = " WHERE vulns.ID={} AND vulns.updated>='{}'".format(
                id, updated
            )
        elif id is not None:
            filter_selection = " WHERE vulns.ID={}".format(id)
        elif updated is not None:
            filter_selection = " WHERE vulns.updated>='{}'".format(updated)

        else:
            filter_selection = ""

        final_query = value_selection + " " + table_selection + filter_selection + ";"
        # self.query["target"] = final_query
        # self.cursor = self.db.cursor()
        # self.cursor.execute(final_query)
        self.targets = [dict(zip(key_names, r)) for r in self.db.query(final_query) if r is not None] 
        return self.targets
        
    def map_types(self, doc):
        """ mapping types and format doc to fit the indexation types"""
        # doc = {k: v for k, v in doc.items() if v != "" or v is not None}
        available_langs = list(self.langs.values())
        # cast and map specific fields separated by '_' and identified by
        # id (except vuln_id)
        # or available lang_lab: fr en
        specific_types_values = [
            (k.split("_"), v)
            for k, v in doc.items()
            if "_" in k and v is not None and isinstance(v, str)
        ]
        text_types = [
            k + [v] for k, v in specific_types_values if k[1] in available_langs
        ]

        # process text fields (_<fr|en>) detecting type and missing lang
        translated_doc = {}
        for key, group in itertools.groupby(text_types, key=lambda x: x[0]):
            # print(key)
            langs = [n[1] for n in list(group)]
            if len(langs) == 1:
                src = langs[0]
                to = [l for l in available_langs if l not in langs][0]
                existing_field_name = "_".join([key, src])

                new_field_name = "_".join([key, to])
                # translate to new lang
                # except for reference
                # try:
                #     translated_doc[new_field_name] = str(
                #         TextBlob(doc[existing_field_name]).translate(
                #             from_lang=src, to=to
                #         )
                #     )
                # except Exception as e:
                    # no translation available: switching back to original
                translated_doc[new_field_name] = doc[existing_field_name]
        # update doc with missing text fields
        doc.update(translated_doc)
        # update doc split ids into array
        id_types = {
            "_".join(k): v.split(",")
            for k, v in specific_types_values
            if k[1] == "id" and k[0] != "vuln"
        }
        if "exploitation_in_the_wild" in doc:
            doc["exploitation_in_the_wild"] = bool(doc["exploitation_in_the_wild"])
            # exploitation_in_the_wild => bool (change in mapping)
            # if doc["exploitation_in_the_wild"] == 1:
            #     doc["exploitation_in_the_wild"] = True
            # else:
            #     doc["exploitation_in_the_wild"] = False
        doc.update(id_types)
        return doc

        
    def build_uuid(self, doc):
        return (
            doc["vuln_id"]
            + doc["os_version_id"]
            + doc["product_id"]
            + doc["editor_id"]
            + doc["os_editor_id"]
        )
    
    @timeit
    def fetch(self, id=None, updated=None):
        """
        fetch documents from the database using mysql.connector
        - select_vulns
        - select_vulns_info
        - select_targets(product, editor, version, os)
        join by vuln_id 
        """
        if self.vulns is None:
            self.select_vulns(id, updated)
        if self.infos is None:
            self.select_infos(id, updated)
        if self.targets is None:
            self.select_targets(id, updated)        
        self.docs = [{**vuln, **info, **target} for target in self.targets for vuln, info in zip(self.vulns, self.infos)]
        return self.docs
        # for vuln, info in zip(self.vulns, self.infos):
        #     for target in self.targets:
        #         yield {**vuln, **info, **target}
                # yield doc
                # if vuln["vuln_id"] == info["vuln_id"] == target["vuln_id"]:
        # return self
        # for vuln, info in zip(self.vulns, self.infos):
        #     for target in self.targets:
        #         # if vuln["vuln_id"] == info["vuln_id"] == target["vuln_id"]:
        #         self.docs.append({**vuln, **info, **target})
        # self.idocs = [(self.build_uuid(doc), doc) for doc in self.docs]
        # return self.idocs

    # @timeit
    def index(self, id=None, updated=None):
        """index item for debug purpose"""
        print("Indexing")
        if self.docs is None:
        print(len(self.idocs))
        # for _id, doc in self.fetch(id, updated):
        #     print(_id,doc)
        #     r = self.es.index(index=self.name, id=_id, body=doc)
        #     print(r)
    @timeit
    def bulk_index(self, id=None, updated=None):
        actions = [
            {"_index": self.name, "_id": _id, "_source": doc}
            for _id, doc in self.fetch(id, updated)
        ]
        res = helpers.bulk(self.es, actions)
        print(res)
       

if __name__ == "__main__":
    # indexing on a daily basis
    today = date.today()
    # set for test
    today = "2020-02-10"
    #corresponds to 10 items and 2353 targets so: 23530 docs in  aprox. 30 sec
    # index_name in settings
    # set for test
    index_name = "vulns_test2"
    i = Indexer(index_name)
    # i.setup()
    # i.select_vulns(updated=today)
    # print(len(i.vulns))
    # i.select_infos(updated=today)
    # print(len(i.infos))
    # i.select_targets(updated=today)
    # print(len(i.targets))
    i.fetch(updated=today)
    print(i.docs)
    # i.index(updated=today)
    # i.bulk_index(updated=today)

import os

from osv import osv
from osv import fields

import openerp

from pygit2 import GIT_SORT_TIME
from pygit2 import Repository


class git_repository(osv.osv):

    _name = 'git.repository'
    _description = 'Git repository.'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
    }

    @property
    def root(self):
        _root = openerp.tools.config.get('git_root')
        if not _root:
            raise osv.except_osv('Root Config', 'Not set.')
        if not os.path.exists(_root):
            raise osv.except_osv('Root Path not Exist', _root)
        return _root

    def get_repo_path(self, repo_name):
        path = os.path.join(self.root, repo_name, '.git')
        if not os.path.exists(path):
            raise osv.except_osv('Repo Path not Exist', path)
        return path

    def get_repo(self, repo_name):
        return Repository(self.get_repo_path(repo_name)) 

    def get_commits(self, repo_name):
        repo = self.get_repo(repo_name)
        for commit in repo.walk(repo.head.oid, GIT_SORT_TIME):
            yield commit

    def update_commits(self, cr, uid, repo):
        for commit in self.get_commits(repo.name):
            # TODO get previous commit in db
            # TODO pass if in db
            # TODO insert new commit in db
            pass

    def delete_commits(self, cr, uid, repo_id):
        # TODO delete all
        # _git_commit = self.pool.get('git_commit')
        # ids = _git_commit.search(cr, uid, [('repo_id', '=', repo_id)])
        # _git_commit.unlink(cr, uid, ids)
        pass

    def create(self, cr, uid, values, context=None):
        _id = super(git_repository, self).create(cr, uid, values,
                                                   context=context)
        repo = self.browse(cr, uid, _id)
        self.update_commits(cr, uid, repo)
        return _id

    def write(self, cr, uid, ids, values, context=None):
        if not super(git_repository, self).write(cr, uid, ids, values,
                                                 context=context):
            return False
        # update commits for the given repositories
        for repo in self.browse(cr, uid, ids):
            self.update_commits(cr, uid, repo)
        return ids

    def unlink(cr, uid, ids, context=None):
        self.delete_commits(cr, uid, ids)
        return super(git_repository, self).unlink(cr, uid, ids, values,
                                                    context=context)


git_repository()

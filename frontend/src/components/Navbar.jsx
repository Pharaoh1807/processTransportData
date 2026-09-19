import React from 'react';
import { Upload, Download, Shield, LogOut, Truck, FileSpreadsheet, RefreshCw, Trash2, Sun, Moon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const Navbar = ({ activeFile, onOpenUpload, onExport, onOpenAdmin, onDeleteFile, isExporting, isDeleting }) => {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();

  return (
    <header className={`sticky top-0 z-40 px-4 py-3 border-b backdrop-blur shadow-md transition-colors duration-200 ${
      isDark ? 'bg-slate-900/90 border-slate-800 text-slate-100' : 'bg-white/90 border-slate-200 text-slate-800'
    }`}>
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">

        {/* Brand Logo & Title */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-blue-600 to-indigo-500 rounded-xl shadow-lg shadow-blue-500/20 text-white">
            <Truck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 bg-clip-text text-transparent">
              SAP Transport Data Analytics
            </h1>
            <p className={`text-xs flex items-center gap-1.5 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              <FileSpreadsheet className="w-3.5 h-3.5 text-blue-500" />
              {activeFile ? (
                <span className="text-blue-500 font-medium">{activeFile.filename} ({activeFile.sheet_name})</span>
              ) : (
                <span>Chưa chọn file dữ liệu SAP</span>
              )}
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2.5">
          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            title={isDark ? "Chuyển sang Chế độ Sáng" : "Chuyển sang Chế độ Tối"}
            className={`p-2 rounded-xl border transition-all ${
              isDark
                ? 'bg-slate-800 border-slate-700 text-amber-400 hover:bg-slate-700'
                : 'bg-slate-100 border-slate-300 text-indigo-600 hover:bg-slate-200'
            }`}
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          <button
            onClick={onOpenUpload}
            className="flex items-center gap-2 px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm rounded-xl shadow-md shadow-blue-600/20 transition duration-150 active:scale-95"
          >
            <Upload className="w-4 h-4" />
            <span>Upload File SAP</span>
          </button>

          {activeFile && (
            <>
              <button
                onClick={onExport}
                disabled={isExporting}
                className="flex items-center gap-2 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 text-white font-medium text-sm rounded-xl shadow-md shadow-emerald-600/20 transition duration-150 active:scale-95"
              >
                {isExporting ? (
                  <RefreshCw className="w-4 h-4 animate-spin text-emerald-200" />
                ) : (
                  <Download className="w-4 h-4" />
                )}
                <span>Xuất Báo Cáo</span>
              </button>

              <button
                onClick={onDeleteFile}
                disabled={isDeleting}
                title="Xóa file hiện tại & dữ liệu khỏi database"
                className="flex items-center gap-2 px-3.5 py-2 bg-rose-600/10 hover:bg-rose-600 border border-rose-500/40 hover:border-rose-500 text-rose-500 hover:text-white font-medium text-sm rounded-xl transition duration-150 active:scale-95 disabled:opacity-50"
              >
                {isDeleting ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Trash2 className="w-4 h-4" />
                )}
                <span>Xóa File</span>
              </button>
            </>
          )}

          {user?.role === 'admin' && (
            <button
              onClick={onOpenAdmin}
              className={`flex items-center gap-1.5 px-3 py-2 border text-xs font-semibold rounded-xl transition ${
                isDark
                  ? 'bg-slate-800 hover:bg-slate-700 text-amber-400 border-amber-500/30'
                  : 'bg-amber-50 hover:bg-amber-100 text-amber-700 border-amber-300'
              }`}
            >
              <Shield className="w-4 h-4 text-amber-500" />
              <span>Quản trị Admin</span>
            </button>
          )}

          {/* User Menu */}
          <div className={`flex items-center gap-2 pl-3 border-l ${isDark ? 'border-slate-800' : 'border-slate-200'}`}>
            <div className="text-right hidden sm:block">
              <p className="text-xs font-semibold">{user?.full_name || user?.email}</p>
              <p className={`text-[10px] capitalize ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{user?.role}</p>
            </div>
            <button
              onClick={logout}
              title="Đăng xuất"
              className={`p-2 rounded-xl transition ${
                isDark ? 'text-slate-400 hover:text-rose-400 hover:bg-slate-800' : 'text-slate-500 hover:text-rose-600 hover:bg-slate-100'
              }`}
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>

      </div>
    </header>
  );
};

export default Navbar;

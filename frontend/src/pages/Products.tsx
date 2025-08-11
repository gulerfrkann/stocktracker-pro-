import React from 'react';

const Products: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Ürünler</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
          Yeni Ürün Ekle
        </button>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">Ürün yönetimi sayfası burada olacak.</p>
      </div>
    </div>
  );
};

export default Products;

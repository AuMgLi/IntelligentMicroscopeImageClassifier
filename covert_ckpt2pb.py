import tensorflow as tf
from tensorflow.python.framework import graph_util
from create_tf_record import *
import tensorflow.contrib.slim.python.slim.nets.inception_v3 as inception_v3


def freeze_graph(input_checkpoint, output_graph):
    '''
    :param input_checkpoint:
    :param output_graph: PB模型保存路径
    :return:
    '''
    # checkpoint = tf.train.get_checkpoint_state(model_folder) #检查目录下ckpt文件状态是否可用
    # input_checkpoint = checkpoint.model_checkpoint_path #得ckpt文件路径

    # 指定输出的节点名称,该节点名称必须是原模型中存在的节点
    output_node_names = "InceptionV3/Logits/SpatialSqueeze"
    saver = tf.train.import_meta_graph(input_checkpoint + '.meta', clear_devices=True)

    with tf.Session() as sess:
        saver.restore(sess, input_checkpoint)  # 恢复图并得到数据
        output_graph_def = graph_util.convert_variables_to_constants(  # 模型持久化，将变量值固定
            sess=sess,
            input_graph_def=sess.graph_def,  # 等于:sess.graph_def
            output_node_names=output_node_names.split(","))  # 如果有多个输出节点，以逗号隔开

        with tf.gfile.GFile(output_graph, "wb") as f:  # 保存模型
            f.write(output_graph_def.SerializeToString())  # 序列化输出
        print("%d ops in the final graph." % len(output_graph_def.node))  # 得到当前图有几个操作节点


def freeze_graph_test(pb_path, image_path):
    '''
    :param pb_path:pb文件的路径
    :param image_path:测试图片的路径
    :return:
    '''
    with tf.Graph().as_default():
        output_graph_def = tf.GraphDef()
        with open(pb_path, "rb") as f:
            output_graph_def.ParseFromString(f.read())
            tf.import_graph_def(output_graph_def, name="")
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            # 定义输入的张量名称,对应网络结构的输入张量
            # input:0作为输入图像,keep_prob:0作为dropout的参数,测试时值为1,is_training:0训练参数
            input_image_tensor = sess.graph.get_tensor_by_name("input:0")
            input_keep_prob_tensor = sess.graph.get_tensor_by_name("keep_prob:0")
            input_is_training_tensor = sess.graph.get_tensor_by_name("is_training:0")

            # 定义输出的张量名称
            output_tensor_name = sess.graph.get_tensor_by_name("InceptionV3/Logits/SpatialSqueeze:0")

            # 读取测试图片
            im = read_image(image_path, 299, 299, normalization=True)
            # print(im)
            print(im.shape)
            im = im[np.newaxis, :]
            print(im.shape)
            # 测试读出来的模型是否正确，注意这里传入的是输出和输入节点的tensor的名字，不是操作节点的名字
            # out=sess.run("InceptionV3/Logits/SpatialSqueeze:0", feed_dict={'input:0': im,'keep_prob:0':1.0,'is_training:0':False})
            out = sess.run(output_tensor_name, feed_dict={input_image_tensor: im,
                                                          input_keep_prob_tensor: 1.0,
                                                          input_is_training_tensor: False})
            print("out:{}".format(out))
            score = tf.nn.softmax(out, name='pre')
            class_id = tf.argmax(score, 1)
            print("pre class_id:{}".format(sess.run(class_id)))


if __name__ == '__main__':
    # 输入ckpt模型路径
    input_checkpoint = 'models/best_models_14400_0.9878.ckpt'
    # 输出pb模型的路径
    out_pb_path = 'models/pb/frozen_model_14400_0.9878.pb'
    # 调用freeze_graph将ckpt转为pb
    # freeze_graph(input_checkpoint, out_pb_path)

    # 验证pb模型
    freeze_graph_test(out_pb_path, 'data/images/test_pb/171248.jpg')
